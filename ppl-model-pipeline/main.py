from src.pipeline import PPLPipeline
import os

if __name__ == "__main__":
    data_path = "data/python_data_1year.csv"
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}. Please run download_data.py first.")
    else:
        pipeline = PPLPipeline(data_path)
        pipeline.run(sample_size=200, epochs=5)
