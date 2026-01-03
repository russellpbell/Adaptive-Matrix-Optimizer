import numpy as np
import tensorflow as tf
from src.modeling import build_image_to_image_model, build_image_to_time_series_model

def test_modeling():
    # Dummy data
    batch_size = 4
    image_size = 32
    channels = 3
    time_steps = 100
    features = 2
    
    input_images = np.random.rand(batch_size, image_size, image_size, channels).astype(np.float32)
    target_images = np.random.rand(batch_size, image_size, image_size, channels).astype(np.float32)
    target_ts = np.random.rand(batch_size, time_steps, features).astype(np.float32)
    
    print("Testing ImageToImageModel...")
    model_i2i = build_image_to_image_model(input_shape=(image_size, image_size, channels), output_channels=channels)
    model_i2i.compile(optimizer='adam', loss='mse')
    output_i2i = model_i2i.predict(input_images)
    print(f"I2I Output shape: {output_i2i.shape}")
    assert output_i2i.shape == (batch_size, image_size, image_size, channels)
    
    print("Testing ImageToTimeSeriesModel...")
    model_i2ts = build_image_to_time_series_model(input_shape=(image_size, image_size, channels), 
                                                  output_length=time_steps, 
                                                  output_features=features)
    model_i2ts.compile(optimizer='adam', loss='mse')
    output_i2ts = model_i2ts.predict(input_images)
    print(f"I2TS Output shape: {output_i2ts.shape}")
    assert output_i2ts.shape == (batch_size, time_steps, features)
    
    print("Modeling tests passed!")

if __name__ == "__main__":
    test_modeling()
