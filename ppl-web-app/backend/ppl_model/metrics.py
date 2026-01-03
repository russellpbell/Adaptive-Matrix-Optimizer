import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from lime import lime_image
from skimage.segmentation import mark_boundaries

def calculate_average_error(y_true, y_pred):
    """
    Calculate average error (MSE and MAE).
    """
    mse = np.mean((y_true - y_pred)**2)
    mae = np.mean(np.abs(y_true - y_pred))
    return mse, mae

def plot_error_distribution(y_true, y_pred, save_path='data/error_distribution.png'):
    """
    Plot the distribution of errors.
    """
    errors = y_true - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(errors.flatten(), kde=True)
    plt.title('Error Distribution')
    plt.xlabel('Error')
    plt.ylabel('Frequency')
    plt.savefig(save_path)
    plt.close()

from lime import lime_tabular
from ppl_model.encoding import create_multichannel_image

def calculate_lime_feature_importance(model, X_windows, feature_names, num_samples=10):
    """
    Calculate LIME importance for each input feature (variable) by wrapping the image encoding.
    
    Args:
        model: Trained Keras model.
        X_windows: Raw input windows (n_samples, window_size, n_features).
        feature_names: List of feature names (e.g. ['XMV(1)', ...]).
        num_samples: Number of samples to explain.
        
    Returns:
        dict: Mapping from feature name to a list of importance weights (collected across samples).
    """
    n_samples, window_size, n_features = X_windows.shape
    
    # Flatten input for Tabular LIME: (n_samples, window_size * n_features)
    X_flat = X_windows.reshape(n_samples, -1)
    
    # Define feature names for flattened array
    # e.g. "XMV(1)_t0", "XMV(1)_t1", ...
    flat_feature_names = []
    for i in range(window_size):
        for feat in feature_names:
            flat_feature_names.append(f"{feat}_t{i}")
            
    # Prediction wrapper: Flat -> Reshape -> Encode -> Predict
    def predict_wrapper(flat_data):
        # flat_data: (n, window_size * n_features)
        n = flat_data.shape[0]
        reshaped = flat_data.reshape(n, window_size, n_features)
        
        # Encode batch
        imgs = []
        for i in range(n):
            # create_multichannel_image expects (window_size, n_features) or (n_features, window_size)?
            # In pipeline we passed: in_window[np.newaxis, :, :] -> (1, window_size, n_features)
            # create_multichannel_image handles (n_samples, timestamps, features)
            # So we can pass 'reshaped' directly if create_multichannel_image supports batch
            # Let's check encoding.py. It supports (n_samples, n_timestamps, n_features).
            pass
            
        # Optimization: Pass whole batch to create_multichannel_image
        encoded_imgs = create_multichannel_image(reshaped, image_size=window_size)
        
        preds = model.predict(encoded_imgs)
        # Reshape for LIME: (n, 1)
        return np.mean(preds, axis=(1, 2)).reshape(-1, 1)

    explainer = lime_tabular.LimeTabularExplainer(
        training_data=X_flat,
        feature_names=flat_feature_names,
        mode='regression',
        discretize_continuous=False # Time series values are continuous
    )
    
    feature_importances = {name: [] for name in feature_names}
    
    print(f"Explaining {min(num_samples, len(X_windows))} samples with LIME...")
    for i in range(min(num_samples, len(X_windows))):
        exp = explainer.explain_instance(
            X_flat[i], 
            predict_wrapper, 
            num_features=len(flat_feature_names), # Get all features
            num_samples=100
        )
        
        # Aggregate weights per variable (summing over time steps)
        # exp.as_list() returns (feature_name, weight)
        # But we can access exp.local_exp[1] (for regression label is usually 1 or 0?)
        # For regression, label is None or 0? LimeTabularExplainer for regression uses label=None?
        # Let's use as_map()
        label = list(exp.local_exp.keys())[0]
        local_exp = exp.local_exp[label] # list of (index, weight)
        
        # Map index back to feature name
        temp_importance = {name: 0.0 for name in feature_names}
        for idx, weight in local_exp:
            # idx maps to flat_feature_names[idx]
            # flat_feature_names structure: t0_f0, t0_f1, ..., t1_f0...
            # Actually my loop was: for t: for feat
            # So idx % n_features gives the feature index
            feat_idx = idx % n_features
            feat_name = feature_names[feat_idx]
            # We take absolute importance? Or raw? 
            # Usually we want to know "how much it affects", so absolute is good for "importance".
            # But user might want direction. Let's store raw weights and let violin show distribution.
            # But summing raw weights over time might cancel out (+ and - effects).
            # Absolute sum is safer for "Importance".
            temp_importance[feat_name] += abs(weight)
            
        for name, val in temp_importance.items():
            feature_importances[name].append(val)
            
    return feature_importances

def plot_lime_violin(feature_importances, save_path='data/lime_violin.png'):
    """
    Plot violin charts of LIME importance per input variable.
    """
    data_to_plot = []
    labels = []
    
    for feat_name, weights in feature_importances.items():
        data_to_plot.append(weights)
        labels.append(feat_name)
        
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=data_to_plot)
    plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45)
    plt.title('Distribution of Feature Importance (LIME)')
    plt.ylabel('Absolute Importance (Aggregated over Time)')
    plt.xlabel('Input Variables')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
