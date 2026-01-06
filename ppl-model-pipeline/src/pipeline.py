import pandas as pd
import numpy as np
import os
import yaml
from src.preprocessing import apply_savitzky_golay
from src.encoding import create_multichannel_image
from src.modeling import build_image_to_time_series_model
from src.metrics import calculate_average_error, plot_error_distribution, calculate_lime_feature_importance, plot_lime_violin, calculate_shap_feature_importance
from statsmodels.tsa.seasonal import seasonal_decompose

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
# from tensorflow.keras.models import clone_model
# from tensorflow.keras.callbacks import EarlyStopping

class PPLPipeline:
    def __init__(self, data_path, output_dir='output'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.scaler = MinMaxScaler()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def clean_and_impute(self, df):
        """
        Imputes missing values using linear interpolation to handle NMAR data better than forward-fill.
        """
        # Interpolate linearly, limit direction both handles leading/trailing if possible, 
        # though time series usually needs strictly past data. 
        # For NMAR sensor data, interpolation often reconstructs trends better than ffill.
        df_imputed = df.interpolate(method='linear', limit_direction='both')
        return df_imputed

    def detect_anomalies(self, df, target_col=None):
        """
        Detects anomalies using STL decomposition residuals.
        """
        if not target_col:
            # Default to first non-timestamp column if not specified
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                target_col = numeric_cols[0]
            else:
                return df # Cannot decompose

        # Ensure no missing values for decomposition
        series = df[target_col].dropna()
        if len(series) < 20: # Need enough data for period
            return df
            
        # Infer period if possible or default. 
        # freq='3min', so daily seasonality might be 24*60/3 = 480 points
        period = 480 if len(series) > 960 else int(len(series)/2) # Fallback
        
        try:
            decomposition = seasonal_decompose(series, model='additive', period=period, extrapolate_trend='freq')
            resid = decomposition.resid
            
            # Simple thresholding: 3 std estimations
            threshold = 3 * np.nanstd(resid)
            anomalies = np.abs(resid) > threshold
            
            # Mark in dataframe
            df['is_anomaly'] = False
            df.loc[series.index, 'is_anomaly'] = anomalies
            
            # Log info
            num_anomalies = anomalies.sum()
            print(f"Detected {num_anomalies} anomalies in {target_col} using STL decomposition.")
            
        except Exception as e:
            print(f"Anomaly detection failed: {e}")
            df['is_anomaly'] = False
            
        return df

    def cross_validate_walk_forward(self, X, y, n_splits=3, epochs=5, log_func=None):
        """
        Performs Walk-Forward Validation (expanding window).
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        # Lazy import
        from tensorflow.keras.models import clone_model
        
        mse_scores = []
        mae_scores = []
        
        if log_func: log_func(f"Starting Walk-Forward Validation with {n_splits} splits...", 5)
        
        fold = 1
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            # Clone model architecture to reset weights
            model_clone = clone_model(self.model)
            model_clone.compile(optimizer='adam', loss='mse')
            
            if log_func: log_func(f"   CV Fold {fold}/{n_splits}...", 5)
            
            # Train
            callbacks_list = []
            if log_func:
                from tensorflow.keras.callbacks import Callback
                class CVProgressCallback(Callback):
                    def on_epoch_end(self, epoch, logs=None):
                       # Log every epoch might be too much for CV if epochs are small? 
                       # Let's log every epoch for now to be safe.
                       log_func(f"   CV Fold {fold}: Epoch {epoch+1}/{epochs} - loss: {logs['loss']:.4f}", 5)
                callbacks_list.append(CVProgressCallback())
                
            model_clone.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=0, callbacks=callbacks_list)
            
            # Evaluate
            y_pred = model_clone.predict(X_test, verbose=0)
            mse, mae = calculate_average_error(y_test, y_pred)
            
            if log_func: log_func(f"   Fold {fold}: MSE={mse:.5f}", 5)
            mse_scores.append(mse)
            mae_scores.append(mae)
            fold += 1
            
        avg_mse = np.mean(mse_scores)
        avg_mae = np.mean(mae_scores)
        if log_func: log_func(f"   Average CV Results - MSE: {avg_mse:.5f}", 5)
        return avg_mse, avg_mae

    def run(self, input_cols=None, output_cols=None, sample_size=100, epochs=5, lime_samples=500, shap_samples=200, window_size=32, run_name=None, status_callback=None, df_override=None):
        def log(msg, step=0, total_steps=6):
            print(msg)
            if status_callback:
                status_callback(msg, step if step is not None else 0, total_steps)

        log("1. Loading Data...", 1)
        if df_override is not None:
             df = df_override.copy()
        else:
             df = pd.read_csv(self.data_path, sep=None, engine='python')
        
        if 'timestamp' not in df.columns:
            # Try to find timestamp column case-insensitive
            cols_lower = [c.lower() for c in df.columns]
            if 'timestamp' in cols_lower:
                ts_col = df.columns[cols_lower.index('timestamp')]
                df.rename(columns={ts_col: 'timestamp'}, inplace=True)
            else:
                df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='3min')

        # Apply Data Quality & Anomaly Detection
        df = self.clean_and_impute(df)
        
        # Detect anomalies on the first potential feature
        potential_features = [c for c in df.columns if c != 'timestamp' and 'Unnamed' not in c]
        if potential_features:
            df = self.detect_anomalies(df, target_col=potential_features[0])

        if input_cols is None or output_cols is None:
            feature_cols = [c for c in df.columns if c != 'timestamp' and 'Unnamed' not in c]
            selected_features = feature_cols[:5]
            input_cols = list(selected_features)
            output_cols = list(selected_features)
            
        # Determine specific output directory for this run
        if run_name:
            current_output_dir = os.path.join(self.output_dir, run_name)
        else:
            current_output_dir = self.output_dir
            
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)
            
        log(f"Output directory: {current_output_dir}")

        all_cols = list(set(input_cols + output_cols))
        data = df[['timestamp'] + all_cols].copy()
        
        log("2. Preprocessing...", 2)
        cols_to_drop = ['timestamp']
        if 'Unnamed: 0' in data.columns:
            cols_to_drop.append('Unnamed: 0')
            
        data_numeric = data.drop(columns=cols_to_drop, errors='ignore')
        data_numeric = data_numeric.select_dtypes(include=[np.number])
        
        log("   Normalizing data...")
        self.feature_cols = data_numeric.columns
        data_scaled = self.scaler.fit_transform(data_numeric)
        data_numeric = pd.DataFrame(data_scaled, columns=self.feature_cols)
        
        smoothed_values = apply_savitzky_golay(data_numeric, window_length=11, polyorder=2)
        smoothed_data = pd.DataFrame(smoothed_values, columns=data_numeric.columns)
        smoothed_data['timestamp'] = data['timestamp'].values
        
        log("3. Encoding...", 3)
        # Use configurable window_size (Process Residence Time)
        # window_size variable is passed in run() args
        n_windows = len(smoothed_data) - window_size
        n_windows = min(n_windows, sample_size)
        
        X_images = []
        y_ts = []
        input_data = smoothed_data[input_cols].values
        output_data = smoothed_data[output_cols].values
        X_windows = []
        
        for i in range(n_windows):
            in_window = input_data[i:i+window_size]
            out_window = output_data[i:i+window_size]
            img = create_multichannel_image(in_window[np.newaxis, :, :], image_size=window_size)
            X_images.append(img[0])
            y_ts.append(out_window)
            X_windows.append(in_window)
            
        self.X_images = np.array(X_images)
        self.y_ts = np.array(y_ts)
        self.X_windows = np.array(X_windows)
        
        log(f"Encoded Input shape: {self.X_images.shape}")
        log(f"Target Output shape: {self.y_ts.shape}")
        
        log("4. Modeling...", 4)
        input_shape = self.X_images.shape[1:]
        output_shape = self.y_ts.shape[1:]
        
        log(f"   Building model with input range {input_shape}...", 4)
        self.model = build_image_to_time_series_model(input_shape, output_shape[0], output_shape[1])
        log("   Model built.", 4)
        
        log("   Compiling model...", 4)
        self.model.compile(optimizer='adam', loss='mse')
        log("   Model compiled.", 4)
        
        # Define Progress Callback
        from tensorflow.keras.callbacks import Callback
        class ProgressCallback(Callback):
            def __init__(self, stage_name):
                super().__init__()
                self.stage_name = stage_name
            def on_epoch_end(self, epoch, logs=None):
                log(f"{self.stage_name}: Epoch {epoch+1}/{epochs} - loss: {logs['loss']:.4f}", 5)

        log("5. Training with Walk-Forward Validation...", 5)
        # 1. Perform Walk-Forward Validation to get metrics
        # Pass callback generator or log function to CV? 
        # For simplicity, let's just log the folds in CV, and detailed epochs in final train.
        mse, mae = self.cross_validate_walk_forward(self.X_images, self.y_ts, epochs=epochs, log_func=log)
        
        # 2. Retrain on Full Data for final artifact
        from tensorflow.keras.callbacks import EarlyStopping
        log("   Retraining on full dataset for final model...")
        es = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
        prog_cb = ProgressCallback("Final Training")
        history = self.model.fit(self.X_images, self.y_ts, epochs=epochs, batch_size=32, verbose=0, callbacks=[es, prog_cb])
        
        # Prediction on full data for analysis (could be overfitting, but used for plots)
        y_pred = self.model.predict(self.X_images, verbose=0)
        
        log(f"Final Validation - MSE: {mse:.5f}, MAE: {mae:.5f}")
        
        # Save static plot (optional backup)
        plot_error_distribution(self.y_ts, y_pred, output_names=output_cols, save_path=os.path.join(current_output_dir, 'error_dist.png'))
        
        log("6. Interpretability (LIME)...", 6)
        context_data, self.lime_importances = calculate_lime_feature_importance(self.model, self.X_windows, input_cols, output_cols, num_samples=min(lime_samples, n_windows))
        
        # Save static plot
        plot_lime_violin(self.lime_importances, save_path=os.path.join(current_output_dir, 'lime_violin.png'))
        
        # Convert LIME dict to DataFrame for App/Controller
        rows = []
        for out_name, feats in self.lime_importances.items():
            for feat_name, weights in feats.items():
                for w in weights:
                    rows.append({
                        'Feature': feat_name,
                        'Importance': w,
                        'Output_Name': out_name
                    })
        self.lime_importances_df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=['Feature', 'Importance', 'Output_Name'])

        # Save LIME Context Data for Controller
        context_df = pd.DataFrame(context_data)
        context_csv_path = os.path.join(current_output_dir, 'lime_context_data.csv')
        context_df.to_csv(context_csv_path, index=False)
        # Calculate SHAP
        log("   Calculating SHAP explanations...", 6)
        # Use simpler sample size for SHAP as it is expensive
        self.shap_df = calculate_shap_feature_importance(self.model, self.X_windows, input_cols, output_cols, num_samples=min(shap_samples, n_windows))
        shap_csv_path = os.path.join(current_output_dir, 'shap_values.csv')
        self.shap_df.to_csv(shap_csv_path, index=False)
        
        # Save LIME Context Data for Controller
        context_df = pd.DataFrame(context_data)
        context_csv_path = os.path.join(current_output_dir, 'lime_context_data.csv')
        context_df.to_csv(context_csv_path, index=False)
        log(f"LIME context data saved to {context_csv_path}")
        
        # Save Model
        model_path = os.path.join(current_output_dir, 'ppl_model.keras')
        self.model.save(model_path)
        log(f"Model saved to {model_path}")
        
        # Save Config (YAML)
        config = {
            'run_name': run_name if run_name else 'default',
            'input_columns': input_cols,
            'output_columns': output_cols,
            'window_size': window_size,
            'sample_size': sample_size,
            'epochs': epochs,
            'final_mse': float(mse),
            'final_mae': float(mae),
            'model_type': 'ImageToTimeSeries',
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        config_path = os.path.join(current_output_dir, 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        log(f"Config saved to {config_path}")
        
        log("Pipeline Run Complete.", 6) # Finish
        
        # Return Comprehensive Results
        return {
            'history': history,
            'mse': mse,
            'mae': mae,
            'y_true': self.y_ts,
            'y_pred': y_pred,
            'lime_importances': self.lime_importances_df,
            'shap_values': self.shap_df,
            'context_data': context_data,
            'X_windows': self.X_windows,
            'config': config,
            'output_dir': current_output_dir,
            'paths': {
                'model': model_path,
                'config': config_path,
                'context': context_csv_path,
                'shap': shap_csv_path
            }
        }

    def evaluate_existing_model(self, model_path, config_path, df_override=None, lime_samples=500, shap_samples=200, status_callback=None):
        """
        Evaluate an already trained model using a provided config and dataset.
        Skips training and jumps to prediction/interpretation.
        """
        def log(msg, step=0):
            print(msg) 
            if status_callback:
                status_callback(msg, step, 5)
            
        # 1. Load Config
        log("Loading Config & Data...", 1)
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        input_cols = config.get('input_columns')
        output_cols = config.get('output_columns')
        window_size = config.get('window_size', 32)
        sample_size = config.get('sample_size', 100)
        
        # 2. Load Data
        if df_override is not None:
             df = df_override.copy()
        else:
             df = pd.read_csv(self.data_path, sep=None, engine='python')
             
        # Timestamp handling (similar to run)
        if 'timestamp' not in df.columns:
            cols_lower = [c.lower() for c in df.columns]
            if 'timestamp' in cols_lower:
                ts_col = df.columns[cols_lower.index('timestamp')]
                df.rename(columns={ts_col: 'timestamp'}, inplace=True)
            else:
                df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='3min')

        # 3. Preprocess (Must replicate run() logic exactly)
        log("Preprocessing Data...", 1)
        df = self.clean_and_impute(df)
        
        # Output Directory (reuse model dir or create temp?)
        current_output_dir = os.path.dirname(model_path)
        
        all_cols = list(set(input_cols + output_cols))
        data = df[['timestamp'] + all_cols].copy()
        
        cols_to_drop = ['timestamp']
        if 'Unnamed: 0' in data.columns:
            cols_to_drop.append('Unnamed: 0')
            
        data_numeric = data.drop(columns=cols_to_drop, errors='ignore')
        data_numeric = data_numeric.select_dtypes(include=[np.number])
        
        # Fit scaler on NEW data (Assumption: User provides representative data)
        self.feature_cols = data_numeric.columns
        data_scaled = self.scaler.fit_transform(data_numeric)
        data_numeric = pd.DataFrame(data_scaled, columns=self.feature_cols)
        
        smoothed_values = apply_savitzky_golay(data_numeric, window_length=11, polyorder=2)
        smoothed_data = pd.DataFrame(smoothed_values, columns=data_numeric.columns)
        smoothed_data['timestamp'] = data['timestamp'].values
        
        # 4. Encoding
        n_windows = len(smoothed_data) - window_size
        n_windows = min(n_windows, sample_size)
        
        X_images = []
        y_ts = []
        input_data = smoothed_data[input_cols].values
        output_data = smoothed_data[output_cols].values
        X_windows = []
        
        for i in range(n_windows):
            in_window = input_data[i:i+window_size]
            out_window = output_data[i:i+window_size]
            img = create_multichannel_image(in_window[np.newaxis, :, :], image_size=window_size)
            X_images.append(img[0])
            y_ts.append(out_window)
            X_windows.append(in_window)
            
        self.X_images = np.array(X_images)
        self.y_ts = np.array(y_ts)
        self.X_windows = np.array(X_windows)
        
        log(f"Encoded Input for Evaluation: {self.X_images.shape}", 1)
        
        # 5. Load Model
        log("Loading Model...", 2)
        # Lazy import
        import tensorflow as tf
        from tensorflow.keras.models import load_model
        
        try:
            # Force CPU (redundant with env but safer for reload)
            tf.config.set_visible_devices([], 'GPU')
        except:
            pass
            
        # Clear existing session to prevent lock contention
        tf.keras.backend.clear_session()
        
        # CPU Enforced in env, but model loading might need care
        self.model = load_model(model_path)
        
        # 6. Predict
        log("Generating Predictions...", 2)
        y_pred = self.model.predict(self.X_images, verbose=0)
        mse, mae = calculate_average_error(self.y_ts, y_pred)
        log(f"Evaluation - MSE: {mse:.5f}, MAE: {mae:.5f}", 3)
        
        # 7. Interpretability
        log("Running LIME Explanation...", 3)
        context_data, self.lime_importances = calculate_lime_feature_importance(self.model, self.X_windows, input_cols, output_cols, num_samples=min(lime_samples, n_windows))
        
        # Convert LIME dict to DataFrame
        rows = []
        for out_name, feats in self.lime_importances.items():
            for feat_name, weights in feats.items():
                for w in weights:
                    rows.append({
                        'Feature': feat_name,
                        'Importance': w,
                        'Output_Name': out_name
                    })
        self.lime_importances_df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=['Feature', 'Importance', 'Output_Name'])

        log("Running SHAP Explanation...", 3)
        self.shap_df = calculate_shap_feature_importance(self.model, self.X_windows, input_cols, output_cols, num_samples=min(shap_samples, n_windows))

        # Return Results (Matching run())
        log("Evaluation Complete", 5)
        return {
            'history': None, # No history for loaded model
            'mse': mse,
            'mae': mae,
            'y_true': self.y_ts,
            'y_pred': y_pred,
            'lime_importances': self.lime_importances_df,
            'shap_values': self.shap_df,
            'context_data': context_data,
            'X_windows': self.X_windows,
            'config': config,
            'output_dir': current_output_dir
        }

    def inverse_transform(self, y_data, cols):
        """
        Inverse transform specific columns of data.
        
        Args:
            y_data (np.ndarray): Data to inverse transform. Shape (n_samples, n_timestamps, n_cols) or (n_timestamps, n_cols).
            cols (list): List of column names corresponding to the last dimension of y_data.
            
        Returns:
            np.ndarray: Inverse transformed data.
        """
        # Handle 2D or 3D input
        original_shape = y_data.shape
        if y_data.ndim == 3:
            # Flatten samples and timestamps
            y_flat = y_data.reshape(-1, len(cols))
        else:
            y_flat = y_data
            
        # Create a placeholder array with all features
        n_rows = y_flat.shape[0]
        n_features = len(self.feature_cols)
        placeholder = np.zeros((n_rows, n_features))
        
        # Map columns to indices
        col_indices = [self.feature_cols.get_loc(c) for c in cols]
        
        # Fill placeholder with provided data
        placeholder[:, col_indices] = y_flat
        
        # Inverse transform
        inversed_placeholder = self.scaler.inverse_transform(placeholder)
        
        # Extract relevant columns
        inversed_data = inversed_placeholder[:, col_indices]
        
        # Reshape back to original
        return inversed_data.reshape(original_shape)
