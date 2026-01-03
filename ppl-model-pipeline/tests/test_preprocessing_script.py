import pandas as pd
import numpy as np
from src.preprocessing import apply_savitzky_golay, inferential_generator
import matplotlib.pyplot as plt

def test_preprocessing():
    # Create dummy data
    t = pd.date_range(start='2023-01-01', periods=100, freq='10min')
    y = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)
    df = pd.DataFrame({'timestamp': t, 'value': y})
    
    # Test Savitzky-Golay
    print("Testing Savitzky-Golay...")
    smoothed = apply_savitzky_golay(df[['value']], window_length=15, polyorder=3)
    
    # Test Inferential Generator (Upsample to 1min)
    print("Testing Inferential Generator...")
    continuous = inferential_generator(df, 'timestamp', target_freq='1min', epochs=10)
    
    print(f"Original shape: {df.shape}")
    print(f"Smoothed shape: {smoothed.shape}")
    print(f"Continuous shape: {continuous.shape}")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['value'], 'o', label='Original (Infrequent)')
    plt.plot(df['timestamp'], smoothed['value'], label='Smoothed')
    plt.plot(continuous.index, continuous['value'], '--', alpha=0.5, label='Continuous (Upsampled)')
    plt.legend()
    plt.savefig('data/preprocessing_test.png')
    print("Saved preprocessing test plot to data/preprocessing_test.png")

if __name__ == "__main__":
    test_preprocessing()
