import pandas as pd
import numpy as np
import os
from ppl_model.preprocessing import apply_savitzky_golay
from ppl_model.encoding import create_multichannel_image
from ppl_model.modeling import build_image_to_time_series_model
from ppl_model.metrics import calculate_average_error, plot_error_distribution, calculate_lime_feature_importance, plot_lime_violin

from sklearn.preprocessing import MinMaxScaler

class PPLPipeline:
    def __init__(self, data_path, output_dir='output'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.scaler = MinMaxScaler()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def run(self, input_cols=None, output_cols=None, sample_size=100, epochs=5):
        print("1. Loading Data...")
        # Load data (assuming CSV for now)
        df = pd.read_csv(self.data_path, sep=';')
        
        if 'timestamp' not in df.columns:
            # Create a dummy timestamp if missing
            df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='3min')
            
        # Determine columns to use
        if input_cols is None or output_cols is None:
            # Default behavior: take first 5 features as both input and output (autoencoder style)
            # Exclude timestamp and unnamed columns
            feature_cols = [c for c in df.columns if c != 'timestamp' and 'Unnamed' not in c]
            selected_features = feature_cols[:5]
            input_cols = list(selected_features)
            output_cols = list(selected_features)
            
        # Combine all needed columns for preprocessing
        all_cols = list(set(input_cols + output_cols))
        data = df[['timestamp'] + all_cols].copy()
        
        print("2. Preprocessing...")
        # Inferential Generator removed per user request
        # continuous_data = inferential_generator(data, 'timestamp', target_freq='1min', epochs=20)
        
        # Savitzky-Golay
        # Apply directly to data (assuming it's already regular enough or we just smooth what we have)
        # Note: Savitzky-Golay requires regular sampling, but if we skip inferential, we assume data is acceptable.
        # We need to drop timestamp for smoothing if it's not numeric
        # We need to drop timestamp for smoothing if it's not numeric
        # Drop timestamp and any unnamed index columns
        cols_to_drop = ['timestamp']
        if 'Unnamed: 0' in data.columns:
            cols_to_drop.append('Unnamed: 0')
            
        data_numeric = data.drop(columns=cols_to_drop, errors='ignore')
        
        # Ensure only numeric
        data_numeric = data_numeric.select_dtypes(include=[np.number])
        
        # Normalize data
        print("   Normalizing data...")
        self.feature_cols = data_numeric.columns
        data_scaled = self.scaler.fit_transform(data_numeric)
        data_numeric = pd.DataFrame(data_scaled, columns=self.feature_cols)
        
        smoothed_values = apply_savitzky_golay(data_numeric, window_length=11, polyorder=2)
        smoothed_data = pd.DataFrame(smoothed_values, columns=data_numeric.columns)
        smoothed_data['timestamp'] = data['timestamp'].values
        
        print("3. Encoding...")
        # Prepare sliding windows for encoding
        window_size = 32 # Corresponds to image size
        n_windows = len(smoothed_data) - window_size
        
        # Limit samples for prototype
        n_windows = min(n_windows, sample_size)
        
        X_images = []
        y_ts = []
        
        # Extract input and output dataframes from smoothed data
        input_data = smoothed_data[input_cols].values
        output_data = smoothed_data[output_cols].values
        
        X_windows = [] # Collect raw windows for LIME
        
        for i in range(n_windows):
            # Input window (to be encoded as image)
            in_window = input_data[i:i+window_size]
            # Output window (time series to predict)
            # We predict the SAME time window as input, or future? 
            # Usually control predicts future, but let's stick to reconstruction/current window for now as per "Inverse Mapping"
            out_window = output_data[i:i+window_size]
            
            # Encode input window to image
            img = create_multichannel_image(in_window[np.newaxis, :, :], image_size=window_size)
            X_images.append(img[0])
            y_ts.append(out_window)
            X_windows.append(in_window)
            
        self.X_images = np.array(X_images)
        self.y_ts = np.array(y_ts)
        self.X_windows = np.array(X_windows)
        
        print(f"Encoded Input shape: {self.X_images.shape}")
        print(f"Target Output shape: {self.y_ts.shape}")
        
        print("4. Modeling...")
        input_shape = self.X_images.shape[1:]
        output_shape = self.y_ts.shape[1:]
        
        # Build model
        # Unpack output_shape tuple (length, features)
        self.model = build_image_to_time_series_model(input_shape, output_shape[0], output_shape[1])
        
        # Compile with MSE for reconstruction/prediction
        self.model.compile(optimizer='adam', loss='mse')
        
        print("5. Training...")
        history = self.model.fit(self.X_images, self.y_ts, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)
        
        # Metrics
        y_pred = self.model.predict(self.X_images)
        mse, mae = calculate_average_error(self.y_ts, y_pred)
        print(f"MSE: {mse}, MAE: {mae}")
        
        plot_error_distribution(self.y_ts, y_pred, save_path=os.path.join(self.output_dir, 'error_dist.png'))
        
        print("6. Interpretability (LIME)...")
        # Explain a few samples using Tabular LIME wrapper
        # Pass raw windows and feature names
        
        self.lime_importances = calculate_lime_feature_importance(self.model, self.X_windows, input_cols, num_samples=1000)
        plot_lime_violin(self.lime_importances, save_path=os.path.join(self.output_dir, 'lime_violin.png'))
        
        # Save Model
        model_path = os.path.join(self.output_dir, 'ppl_model.h5')
        self.model.save(model_path)
        print(f"Model saved to {model_path}")
        
        print("Pipeline Run Complete.")
        return history, mse

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
