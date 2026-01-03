import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def apply_savitzky_golay(data, window_length=11, polyorder=2):
    """
    Apply Savitzky-Golay filter to smooth data.
    
    Args:
        data (pd.DataFrame or np.ndarray): Input data.
        window_length (int): The length of the filter window (i.e., the number of coefficients).
        polyorder (int): The order of the polynomial used to fit the samples.
        
    Returns:
        pd.DataFrame or np.ndarray: Smoothed data.
    """
    if isinstance(data, pd.DataFrame):
        # Apply to each column
        smoothed_data = data.copy()
        for col in data.columns:
            # window_length must be odd and less than or equal to the size of data
            wl = min(window_length, len(data))
            if wl % 2 == 0:
                wl -= 1
            if wl < polyorder + 2:
                 # Fallback or skip if data is too short
                 continue
            smoothed_data[col] = savgol_filter(data[col], wl, polyorder)
        return smoothed_data
    else:
        wl = min(window_length, len(data))
        if wl % 2 == 0:
            wl -= 1
        return savgol_filter(data, wl, polyorder)

def inferential_generator(data, time_col, target_freq='1min', epochs=50):
    """
    Generate a continuous time series from infrequent data using a Neural Network regression.
    
    Args:
        data (pd.DataFrame): Input dataframe with a time column.
        time_col (str): Name of the time column.
        target_freq (str): Target frequency for resampling (e.g., '1min', '1H').
        epochs (int): Number of training epochs for the regression model.
        
    Returns:
        pd.DataFrame: Continuous time series.
    """
    import tensorflow as tf
    from tensorflow.keras import layers, models
    
    # Ensure time column is datetime
    data = data.copy()
    data[time_col] = pd.to_datetime(data[time_col])
    
    # Convert time to numeric (seconds from start)
    start_time = data[time_col].min()
    data['time_numeric'] = (data[time_col] - start_time).dt.total_seconds()
    
    # Normalize time
    time_max = data['time_numeric'].max()
    X_train = data[['time_numeric']].values / time_max
    
    # Target variables (all other columns)
    target_cols = [c for c in data.columns if c not in [time_col, 'time_numeric']]
    y_train = data[target_cols].values
    
    # Build a simple MLP for regression
    model = models.Sequential([
        layers.Dense(64, activation='relu', input_shape=(1,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(len(target_cols))
    ])
    
    model.compile(optimizer='adam', loss='mse')
    
    # Train model
    print("Training Inferential Generator (NN)...")
    model.fit(X_train, y_train, epochs=epochs, verbose=0)
    
    # Generate continuous timeline
    full_range = pd.date_range(start=start_time, end=data[time_col].max(), freq=target_freq)
    full_time_numeric = (full_range - start_time).total_seconds().values.reshape(-1, 1)
    X_pred = full_time_numeric / time_max
    
    # Predict
    y_pred = model.predict(X_pred)
    
    # Create result DataFrame
    continuous_data = pd.DataFrame(y_pred, columns=target_cols)
    continuous_data[time_col] = full_range
    continuous_data = continuous_data.set_index(time_col)
    
    return continuous_data
