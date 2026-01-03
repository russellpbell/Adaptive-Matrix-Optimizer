import numpy as np
import tensorflow as tf
from src.metrics import calculate_average_error, plot_error_distribution, calculate_lime_feature_importance, plot_lime_violin
from src.modeling import build_image_to_time_series_model

def test_metrics():
    # Dummy data
    n_samples = 5
    image_size = 32
    channels = 3
    time_steps = 10
    features = 1
    
    y_true = np.random.randn(n_samples, time_steps, features)
    y_pred = y_true + np.random.normal(0, 0.1, (n_samples, time_steps, features))
    
    # Generate raw windows for LIME test
    # (n_samples, window_size, n_features)
    # window_size should match image_size for encoding
    X_windows = np.random.rand(n_samples, image_size, features)
    feature_names = ['Feature_1']
    
    # Test Error Calculation
    mse, mae = calculate_average_error(y_true, y_pred)
    print(f"MSE: {mse}, MAE: {mae}")
    
    # Test Error Plot
    plot_error_distribution(y_true, y_pred, save_path='data/test_error_dist.png')
    print("Saved error distribution plot.")
    
    # Test LIME
    print("Testing LIME...")
    # Model input shape: (image_size, image_size, channels)
    # For univariate (1 feature), channels=3.
    model = build_image_to_time_series_model((image_size, image_size, channels), time_steps, features)
    
    # LIME needs a trained model, but random weights are fine for testing the pipeline
    importances = calculate_lime_feature_importance(model, X_windows, feature_names, num_samples=2)
    print(f"Generated importances for {len(importances)} features.")
    
    # Test LIME Plot
    plot_lime_violin(importances, save_path='data/test_lime_violin.png')
    print("Saved LIME violin plot.")

if __name__ == "__main__":
    test_metrics()
