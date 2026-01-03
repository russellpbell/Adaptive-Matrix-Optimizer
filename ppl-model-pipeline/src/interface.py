import argparse
import os
import matplotlib.pyplot as plt
from src.pipeline import PPLPipeline

def main():
    parser = argparse.ArgumentParser(description="PPL Model Pipeline CLI")
    
    parser.add_argument('--data', type=str, default='data/python_data_1year.csv', help='Path to dataset CSV')
    parser.add_argument('--samples', type=int, default=100, help='Number of windows to process')
    parser.add_argument('--epochs', type=int, default=5, help='Number of training epochs')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    parser.add_argument('--setpoint', type=float, default=0.0, help='Controller setpoint (not fully integrated into pipeline logic yet)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"Error: Data file not found at {args.data}")
        return

    print(f"Starting PPL Pipeline with:")
    print(f"  Data: {args.data}")
    print(f"  Samples: {args.samples}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Output: {args.output}")
    
    pipeline = PPLPipeline(args.data, output_dir=args.output)
    
    # Run pipeline
    history, mse = pipeline.run(sample_size=args.samples, epochs=args.epochs)
    
    print("\nPipeline execution finished.")
    print(f"Final MSE: {mse}")
    print(f"Check {args.output} for results.")

if __name__ == "__main__":
    main()
