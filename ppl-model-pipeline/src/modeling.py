
# Lazy load imports to avoid mutex locks on startup
# import tensorflow as tf
# from tensorflow.keras import layers, models

def _get_tf():
    """Lazy loader for TensorFlow with forced CPU usage."""
    print("DEBUG: _get_tf called. Setting env vars...", flush=True)
    import os
    # Force CPU to avoid Metal/Lock issues
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 
    print(f"DEBUG: CUDA_VISIBLE_DEVICES is currently: {os.environ.get('CUDA_VISIBLE_DEVICES')}", flush=True)
    import tensorflow as tf
    print("DEBUG: TensorFlow imported. Setting visible devices...", flush=True)
    try:
        # Explicitly disable GPU devices if visible
        tf.config.set_visible_devices([], 'GPU')
    except:
        pass
    print("DEBUG: Visible devices set. Returning tf.", flush=True)
    return tf

def build_image_to_image_model(input_shape, output_channels=3):
    """
    Build a model that maps input images (Control) to output images (Controlled).
    Using a simple Autoencoder/UNet-like structure.
    
    Args:
        input_shape (tuple): Shape of input image (height, width, channels).
        output_channels (int): Number of channels in output image.
        
    Returns:
        tf.keras.Model: The constructed model.
    """
    tf = _get_tf()
    from tensorflow.keras import layers, models
    
    inputs = layers.Input(shape=input_shape)
    
    # Encoder
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    encoded = layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Decoder
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(encoded)
    x = layers.UpSampling2D((2, 2))(x)
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = layers.UpSampling2D((2, 2))(x)
    outputs = layers.Conv2D(output_channels, (3, 3), activation='sigmoid', padding='same')(x)
    
    model = models.Model(inputs, outputs, name="ImageToImageModel")
    return model

def build_image_to_time_series_model(input_shape, output_length, output_features):
    """
    Build a model that maps images to time series (Inverse Mapping).
    
    Args:
        input_shape (tuple): Shape of input image (height, width, channels).
        output_length (int): Length of the output time series.
        output_features (int): Number of features in the output time series.
        
    Returns:
        tf.keras.Model: The constructed model.
    """
    tf = _get_tf()
    from tensorflow.keras import layers, models

    inputs = layers.Input(shape=input_shape)
    
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)
    
    # Output layer: Flattened time series
    x = layers.Dense(output_length * output_features)(x)
    outputs = layers.Reshape((output_length, output_features))(x)
    
    model = models.Model(inputs, outputs, name="ImageToTimeSeriesModel")
    return model

def get_controller_objective(setpoint=0.0):
    """
    Factory for Controller Objective Function.
    Returns a loss function that minimizes deviation from a setpoint.
    
    Args:
        setpoint: Target value for the controlled variables.
        
    Returns:
        function: Loss function accepting (y_true, y_pred).
    """
    tf = _get_tf()
    
    def controller_loss(y_true, y_pred):
        # Calculate squared deviation from setpoint
        # We assume y_pred is the controlled variable trajectory
        return tf.reduce_mean(tf.square(y_pred - setpoint))
        
    return controller_loss
