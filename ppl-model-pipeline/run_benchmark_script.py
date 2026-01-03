import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.pipeline import PPLPipeline
from src.benchmark import Benchmarker

if __name__ == "__main__":
    print("Initializing Pipeline...")
    # Use relative path to data
    data_path = "ppl-model-pipeline/data/python_data_1year.csv"
    pipeline = PPLPipeline(data_path=data_path, output_dir="output/benchmark_run")
    
    print("Initializing Benchmarker...")
    benchmarker = Benchmarker(pipeline)
    
    # Define columns
    input_cols = ['XMEAS(1)', 'XMEAS(2)', 'XMEAS(3)', 'XMEAS(4)', 'XMEAS(5)']
    output_cols = ['XMEAS(6)']
    
    print("Running Benchmark...")
    # Small sample size for speed in verification
    benchmarker.run_benchmark(input_cols, output_cols, sample_size=200, epochs=2)
    print("Benchmark Comparison Complete.")
