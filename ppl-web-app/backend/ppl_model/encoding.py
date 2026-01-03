import numpy as np
from pyts.image import GramianAngularField, MarkovTransitionField

def encode_gasf_gadf(time_series, image_size=32, method='summation'):
    """
    Encode time series into Gramian Angular Field (GASF or GADF).
    
    Args:
        time_series (np.ndarray): Input time series of shape (n_samples, n_timestamps).
        image_size (int): Size of the output image.
        method (str): 'summation' for GASF, 'difference' for GADF.
        
    Returns:
        np.ndarray: Encoded images of shape (n_samples, image_size, image_size).
    """
    gaf = GramianAngularField(image_size=image_size, method=method)
    return gaf.fit_transform(time_series)

def encode_mtf(time_series, image_size=32, n_bins=8, strategy='quantile'):
    """
    Encode time series into Markov Transition Field (MTF).
    
    Args:
        time_series (np.ndarray): Input time series of shape (n_samples, n_timestamps).
        image_size (int): Size of the output image.
        n_bins (int): Number of bins for discretization.
        strategy (str): Strategy for discretization ('uniform', 'quantile', 'normal').
        
    Returns:
        np.ndarray: Encoded images of shape (n_samples, image_size, image_size).
    """
    mtf = MarkovTransitionField(image_size=image_size, n_bins=n_bins, strategy=strategy)
    return mtf.fit_transform(time_series)

def create_multichannel_image(time_series, image_size=32):
    """
    Create a multi-channel image combining GASF, GADF, and MTF.
    Supports both univariate (n_samples, n_timestamps) and multivariate (n_samples, n_timestamps, n_features) input.
    
    Args:
        time_series (np.ndarray): Input time series.
        image_size (int): Size of the output image.
        
    Returns:
        np.ndarray: Combined images. 
                    If univariate: (n_samples, image_size, image_size, 3).
                    If multivariate: (n_samples, image_size, image_size, n_features * 3).
    """
    # Handle multivariate case: (n_samples, n_timestamps, n_features)
    if time_series.ndim == 3:
        n_samples, n_timestamps, n_features = time_series.shape
        all_channels = []
        for i in range(n_features):
            # Extract univariate series: (n_samples, n_timestamps)
            ts_univariate = time_series[:, :, i]
            
            gasf = encode_gasf_gadf(ts_univariate, image_size=image_size, method='summation')
            gadf = encode_gasf_gadf(ts_univariate, image_size=image_size, method='difference')
            mtf = encode_mtf(ts_univariate, image_size=image_size)
            
            # Stack these 3 for this feature
            # gasf: (n_samples, image_size, image_size)
            # We want (n_samples, image_size, image_size, 3)
            channels = np.stack([gasf, gadf, mtf], axis=-1)
            all_channels.append(channels)
            
        # Concatenate all features along channel axis
        # Result: (n_samples, image_size, image_size, n_features * 3)
        return np.concatenate(all_channels, axis=-1)
        
    # Handle univariate case: (n_samples, n_timestamps)
    else:
        gasf = encode_gasf_gadf(time_series, image_size=image_size, method='summation')
        gadf = encode_gasf_gadf(time_series, image_size=image_size, method='difference')
        mtf = encode_mtf(time_series, image_size=image_size)
        
        # Stack along the last axis
        return np.stack([gasf, gadf, mtf], axis=-1)
