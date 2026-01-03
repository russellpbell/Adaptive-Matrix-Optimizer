import pandas as pd
import numpy as np
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from src.pipeline import PPLPipeline

class Benchmarker:
    def __init__(self, pipeline: PPLPipeline):
        self.pipeline = pipeline

    def run_holt_winters(self, series, n_splits=3):
        """
        Runs Holt-Winters Exponential Smoothing with Walk-Forward Validation on a single series.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        mse_scores = []
        mae_scores = []
        
        # Ensure numeric
        series = pd.to_numeric(series, errors='coerce').fillna(method='bfill')
        
        for train_index, test_index in tscv.split(series):
            train, test = series.iloc[train_index], series.iloc[test_index]
            
            try:
                # Seasonal period is a guess, using 12 for small test or inferred
                model = ExponentialSmoothing(train, seasonal='add', seasonal_periods=12, initialization_method="estimated").fit()
                pred = model.forecast(len(test))
                
                mse = mean_squared_error(test, pred)
                mae = mean_absolute_error(test, pred)
                
                mse_scores.append(mse)
                mae_scores.append(mae)
            except Exception as e:
                print(f"Holt-Winters failed for split: {e}")
                mse_scores.append(np.nan)
                mae_scores.append(np.nan)
                
        return np.nanmean(mse_scores), np.nanmean(mae_scores)

    def run_benchmark(self, input_cols, output_cols, sample_size=100, epochs=5):
        """
        Compares LSTM (from Pipeline) vs Holt-Winters.
        """
        results = []
        
        # 1. Run LSTM Pipeline
        print("Running LSTM Benchmark...")
        lstm_res = self.pipeline.run(input_cols=input_cols, output_cols=output_cols, sample_size=sample_size, epochs=epochs, run_name="benchmark_lstm")
        lstm_mse = lstm_res['mse']
        lstm_mae = lstm_res['mae']
        
        results.append({
            'Model': 'LSTM (Deep Learning)',
            'MSE': lstm_mse,
            'MAE': lstm_mae,
            'Notes': 'Multivariate, capturing complex interactions'
        })
        
        # 2. Run Holt-Winters (Univariate for each output column)
        print("Running Holt-Winters Benchmark...")
        # Get data through pipeline steps until encoding to get the smoothed/scaled data?
        # Or just use raw data? The briefing implies "prioritize Classical for simple data".
        # Let's use the preprocessed data available in the pipeline if possible, or reload.
        
        # Accessing data from pipeline (assuming it ran) - but run() returns results. 
        # We need the dataframe. Let's look at how pipeline loads data.
        df = pd.read_csv(self.pipeline.data_path)
        # Apply same cleaning
        df = self.pipeline.clean_and_impute(df)
        
        # We need to scale to be comparable to LSTM? 
        # LSTM error is calculated on Scaled data [0,1].
        # So we MUST run HW on scaled data to compare MSE directly.
        
        # Re-use scaler from pipeline
        if hasattr(self.pipeline, 'scaler'):
            # This requires pipeline to have fit the scaler.
            # But we just ran pipeline.run(), so self.pipeline.scaler is fit.
            pass
            
        # Extract output cols from df, scale them
        data_numeric = df.select_dtypes(include=[np.number])
        # We need to map columns correctly. Pipeline scales ALL numeric columns.
        # It's safer to reproduce the preprocessing steps
        
        # Step 1: Filter columns
        cols_to_drop = ['timestamp', 'Unnamed: 0']
        data_numeric = data_numeric.drop(columns=cols_to_drop, errors='ignore')
        
        # Step 2: Scale
        scaled_data = self.pipeline.scaler.transform(data_numeric)
        data_scaled_df = pd.DataFrame(scaled_data, columns=data_numeric.columns)
        
        hw_mse_list = []
        hw_mae_list = []
        
        for col in output_cols:
            if col in data_scaled_df.columns:
                mse, mae = self.run_holt_winters(data_scaled_df[col])
                hw_mse_list.append(mse)
                hw_mae_list.append(mae)
        
        avg_hw_mse = np.nanmean(hw_mse_list)
        avg_hw_mae = np.nanmean(hw_mae_list)
        
        results.append({
            'Model': 'Holt-Winters (Classical)',
            'MSE': avg_hw_mse,
            'MAE': avg_hw_mae,
            'Notes': 'Univariate, computationally efficient'
        })
        
        # Generate Report
        self.generate_report(results, self.pipeline.output_dir)
        
        return results

    def generate_report(self, results, output_dir):
        report_path = os.path.join(output_dir, "benchmark_results.md")
        with open(report_path, "w") as f:
            f.write("# Model Benchmark Report\n\n")
            f.write("| Model | MSE | MAE | Notes |\n")
            f.write("|-------|-----|-----|-------|\n")
            for r in results:
                f.write(f"| {r['Model']} | {r['MSE']:.5f} | {r['MAE']:.5f} | {r['Notes']} |\n")
            
            f.write("\n\n## Recommendation\n")
            best_model = min(results, key=lambda x: x['MSE'])
            f.write(f"Based on MSE, the best model is **{best_model['Model']}**.\n")
            
            if best_model['Model'] == 'Holt-Winters (Classical)':
                f.write("Classical methods outperformed Deep Learning. This suggests the data structure is relatively simple or linear, saving significant compute.\n")
            else:
                f.write("LSTM outperformed Classical methods, justifying the extra compute for capturing complex non-linear patterns.\n")
                
        print(f"Benchmark report saved to {report_path}")
