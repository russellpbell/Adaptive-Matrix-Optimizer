import numpy as np
import pandas as pd
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

def plot_error_distribution(y_true, y_pred, output_names=None, save_path='data/error_distribution.png'):
    """
    Plot the distribution of errors for each output variable.
    """
    errors = y_true - y_pred
    # errors shape: (n_samples, n_outputs) OR (n, window, n_outputs)
    # Assume (n, n_outputs) for simplicity of plotting, or flatten over time
    
    if errors.ndim == 3:
        # (n, window, outputs) -> flatten time -> (n*window, outputs)
        errors = errors.reshape(-1, errors.shape[-1])
    elif errors.ndim == 1:
        errors = errors.reshape(-1, 1)
        
    n_outputs = errors.shape[1]
    
    # Create subplots
    fig, axes = plt.subplots(n_outputs, 1, figsize=(10, 6 * n_outputs), squeeze=False)
    
    for i in range(n_outputs):
        ax = axes[i, 0]
        col_name = output_names[i] if output_names and i < len(output_names) else f"Output {i+1}"
        
        sns.histplot(errors[:, i], kde=True, ax=ax)
        ax.set_title(f'Error Distribution - {col_name}')
        ax.set_xlabel('Error')
        ax.set_ylabel('Frequency')
        
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

# ... LIME part ...
from lime import lime_tabular
import shap
from src.encoding import create_multichannel_image

def calculate_shap_feature_importance(model, X_windows, feature_names, output_names, num_samples=50, status_callback=None):
    """
    Calculate SHAP values for each input feature towards each output variable.
    Returns structured DataFrame for Visualization.
    """
    n_samples, window_size, n_features = X_windows.shape
    X_flat = X_windows.reshape(n_samples, -1) # (N, Win*Feat)
    
    # Background for SHAP (KMeans summary)
    # Use up to 50 samples for background
    background_data = shap.kmeans(X_flat, min(50, len(X_flat)))
    
    shap_results = []
    
    total_samples = min(num_samples, len(X_flat))
    if status_callback:
        status_callback(f"Initializing SHAP Explainer ({total_samples} samples)...")
        
    for out_idx, out_name in enumerate(output_names):
        def predict_wrapper(flat_data):
            # Same wrapper as LIME
            n = flat_data.shape[0]
            reshaped = flat_data.reshape(n, window_size, n_features)
            imgs = []
            for i in range(n):
                single_window = reshaped[i]
                img = create_multichannel_image(single_window[np.newaxis, :, :], image_size=window_size)
                imgs.append(img[0])
            imgs = np.array(imgs)
            preds = model.predict(imgs, verbose=0)
            mean_preds = np.mean(preds, axis=1) 
            return mean_preds[:, out_idx]

        # Use KernelExplainer
        explainer = shap.KernelExplainer(predict_wrapper, background_data)
        
        # Explain samples iteratively to report progress
        samples_to_explain = X_flat[:total_samples]
        
        # Collect shap values for all samples for this output
        # shape: (n_samples, n_features_flat)
        output_shap_values = []
        
        for i in range(total_samples):
            # Report Progress
            # We have len(output_names) outputs. 
            # Current progress = (out_idx * total_samples) + i
            # Total steps = len(output_names) * total_samples
            overall_current = (out_idx * total_samples) + i + 1
            overall_total = len(output_names) * total_samples
            percent = int((overall_current / overall_total) * 100)
            
            if status_callback:
                status_callback(f"SHAP Explaining: {overall_current}/{overall_total} ({percent}%) - Output: {out_name}")
            
            # Explain single instance (reshape to 2D for shap)
            # exp_val is list of arrays? No, KernelExplainer for scalar output returns array.
            # nsamples=100 is low but fast for UI.
            val = explainer.shap_values(samples_to_explain[i:i+1], nsamples=100) 
            # val is (1, n_features_flat) or list if multi-output (but we wrapper for single output)
            
            if isinstance(val, list):
                output_shap_values.append(val[0])
            else:
                output_shap_values.append(val)
                
        # Concatenate
        combined_shap = np.vstack(output_shap_values) # (N, Win*Feat)
        
        # Aggregate SHAP values back to Feature Level (Sum across time window)
        for i in range(total_samples):
            # X_flat[i] corresponds to sample i
            row_shap = combined_shap[i] # (Win*Feat,)
            sample_in = X_flat[i]     # (Win*Feat,)
            
            # Reshape to (Window, Feat)
            shap_matrix = row_shap.reshape(window_size, n_features)
            in_matrix = sample_in.reshape(window_size, n_features)
            
            # Sum across time (axis 0) -> (Feat,)
            # This gives "Total SHAP impact of Feature F over the window"
            total_shap = np.sum(shap_matrix, axis=0)
            mean_input = np.mean(in_matrix, axis=0) # Average value of feature F
            
            for f_idx, feat in enumerate(feature_names):
                shap_results.append({
                    'Sample_ID': i,
                    'Output_Name': out_name,
                    'Feature': feat,
                    'Feature_Value': mean_input[f_idx],
                    'SHAP_Value': total_shap[f_idx]
                })

    return pd.DataFrame(shap_results)

def calculate_lime_feature_importance(model, X_windows, feature_names, output_names, num_samples=10):
    """
    Calculate LIME importance and Gains for each input feature towards each output variable.
    Returns structured data for Controller Context.
    """
    n_samples, window_size, n_features = X_windows.shape
    X_flat = X_windows.reshape(n_samples, -1)
    
    flat_feature_names = []
    for i in range(window_size):
        for feat in feature_names:
            flat_feature_names.append(f"{feat}_t{i}")
            
    explainer = lime_tabular.LimeTabularExplainer(
        training_data=X_flat,
        feature_names=flat_feature_names,
        mode='regression',
        discretize_continuous=False
    )
    
    context_data = []
    # visualization_importances = { output_name: { feat: [] } }
    visualization_importances = {out: {name: [] for name in feature_names} for out in output_names}
    
    for out_idx, out_name in enumerate(output_names):
        
        def predict_wrapper(flat_data):
            n = flat_data.shape[0]
            reshaped = flat_data.reshape(n, window_size, n_features)
            imgs = []
            for i in range(n):
                single_window = reshaped[i]
                img = create_multichannel_image(single_window[np.newaxis, :, :], image_size=window_size)
                imgs.append(img[0])
            imgs = np.array(imgs)
            preds = model.predict(imgs, verbose=0)
            mean_preds = np.mean(preds, axis=1) # (n, n_outputs)
            return mean_preds[:, out_idx]

        print(f"Explaining Output '{out_name}' ({min(num_samples, len(X_windows))} samples)...")
        
        for i in range(min(num_samples, len(X_windows))):
            exp = explainer.explain_instance(
                X_flat[i], 
                predict_wrapper, 
                num_features=len(flat_feature_names),
                num_samples=100
            )
            
            available_keys = list(exp.local_exp.keys())
            local_exp = exp.local_exp[available_keys[0]]
            
            sample_gains = {feat: 0.0 for feat in feature_names}
            
            for idx, weight in local_exp:
                feat_idx = idx % n_features
                feat_name = feature_names[feat_idx]
                sample_gains[feat_name] += weight
                
            row = {
                'Sample_ID': i,
                'Output_Name': out_name
            }
            
            current_window = X_windows[i]
            input_means = np.mean(current_window, axis=0)
            for f_idx, f_name in enumerate(feature_names):
                row[f"Input_{f_name}"] = input_means[f_idx]
                row[f"Gain_{f_name}"] = sample_gains[f_name]
                
                # Add to visualization dict FOR THIS OUTPUT
                visualization_importances[out_name][f_name].append(abs(sample_gains[f_name]))

            context_data.append(row)
            
    return context_data, visualization_importances

def plot_lime_violin(visualization_importances, save_path='data/lime_violin.png'):
    """
    Plot violin charts of LIME importance per input variable, separated by output variable.
    visualization_importances: dict { output_name: { feature_name: [weights] } }
    """
    # Flatten data for plotting with Hue
    # Dataframe: Feature, Importance, Output
    rows = []
    
    for out_name, feats in visualization_importances.items():
        for feat_name, weights in feats.items():
            for w in weights:
                rows.append({
                    'Feature': feat_name,
                    'Importance': w,
                    'Output': out_name
                })
                
    if not rows:
        return
        
    df_plot = pd.DataFrame(rows)
    
    plt.figure(figsize=(14, 8))
    sns.violinplot(data=df_plot, x='Feature', y='Importance', hue='Output', split=True)
    plt.title('Distribution of Feature Importance (LIME) per Output')
    plt.ylabel('Absolute Importance (Aggregated over Time)')
    plt.xlabel('Input Variables')
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
