import os
import pandas as pd
import numpy as np
import random

# Global
_df = None
_numeric_cols = []

def get_data():
    global _df, _numeric_cols
    if _df is None:
        print("Loading Tennessee Eastman Dataset...")
        # Resolve path relative to this backend file
        # Expected: ppl-web-app/backend/../../ppl-model-pipeline/data/python_data_1year.csv
        # Or just use the one I found: ppl-model-pipeline/data/python_data_1year.csv
        
        # Current dir: .../ppl-web-app/backend
        # Target: .../ppl-model-pipeline/data/python_data_1year.csv
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.abspath(os.path.join(base_dir, "../../ppl-model-pipeline/data/python_data_1year.csv"))
        
        if not os.path.exists(data_path):
            print(f"Error: Data file not found at {data_path}")
            # Fallback to backend/data if copied there? 
            # Found: ppl-web-app/backend/data/python_data_1year.csv earlier
            data_path = os.path.join(base_dir, "data", "python_data_1year.csv")
            
        print(f"Reading from {data_path}")
        try:
            _df = pd.read_csv(data_path, sep=';')
             # Timestamp adjustment if needed
            if 'timestamp' not in _df.columns:
                _df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(_df), freq='3min')
            
            # Filter numeric
            cols_to_drop = ['timestamp', 'Unnamed: 0']
            for c in cols_to_drop:
                if c in _df.columns:
                    _df.drop(columns=[c], inplace=True)
            
            _numeric_cols = _df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"Loaded {_df.shape} with {len(_numeric_cols)} numeric variables.")
            
        except Exception as e:
            print(f"Failed to load data: {e}")
            _df = pd.DataFrame() # Empty fallback
            
    return _df

def get_available_variables():
    get_data()
    return _numeric_cols

def predict_sample(variable_name: str):
    df = get_data()
    if df.empty or variable_name not in df.columns:
        return None
        
    # Get a random window
    window_size = 100
    max_idx = len(df) - window_size
    start_idx = random.randint(0, max_idx)
    
    actual_series = df[variable_name].iloc[start_idx:start_idx+window_size].values
    
    # Simulate prediction (Actual + Noise)
    # Scale of noise related to std dev of the series
    std_dev = np.std(actual_series)
    noise = np.random.normal(0, std_dev * 0.1, size=window_size)
    predicted_series = actual_series + noise
    
    time_steps = list(range(window_size))
    
    return {
        variable_name: {
            "actual": actual_series.tolist(),
            "predicted": predicted_series.tolist(),
            "time_steps": time_steps
        }
    }
