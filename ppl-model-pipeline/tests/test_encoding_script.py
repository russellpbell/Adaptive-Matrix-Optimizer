import numpy as np
import matplotlib.pyplot as plt
from src.encoding import create_multichannel_image

def test_encoding():
    # Create dummy time series data
    # Shape: (n_samples, n_timestamps)
    n_samples = 5
    n_timestamps = 100
    time_series = np.random.randn(n_samples, n_timestamps)
    
    # Add some pattern
    t = np.linspace(0, 4*np.pi, n_timestamps)
    time_series += np.sin(t)
    
    print("Encoding time series to images...")
    images = create_multichannel_image(time_series, image_size=32)
    
    print(f"Input shape: {time_series.shape}")
    print(f"Output images shape: {images.shape}")
    
    # Plot the first sample's channels
    plt.figure(figsize=(12, 4))
    titles = ['GASF', 'GADF', 'MTF']
    for i in range(3):
        plt.subplot(1, 3, i+1)
        plt.imshow(images[0, :, :, i], cmap='rainbow', origin='lower')
        plt.title(titles[i])
        plt.colorbar()
    
    plt.tight_layout()
    plt.savefig('data/encoding_test.png')
    print("Saved encoding test plot to data/encoding_test.png")

if __name__ == "__main__":
    test_encoding()
