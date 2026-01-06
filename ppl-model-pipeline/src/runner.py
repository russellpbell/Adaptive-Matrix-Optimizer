import os
import sys

# Force CPU usage BEFORE any heavy imports to prevent macOS Metal/Lock issues
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Pre-import TensorFlow to manage BLAS contentions on macOS
try:
    import tensorflow as tf
    # Explicitly disable GPU visibility
    tf.config.set_visible_devices([], 'GPU')
except ImportError:
    pass

import argparse
import pickle
import yaml
import pandas as pd
import numpy as np

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lazy import pipeline to avoid heavy startup cost if just checking args
from src.pipeline import PPLPipeline

def status_printer(msg, step, total):
    """
    Format: STATUS|step|total|message
    App can parse this to update UI.
    """
    print(f"STATUS|{step}|{total}|{msg}", flush=True)

def train(args):
    status_printer("Initializing Worker...", 0, 5)
    
    # Load Data
    # For simplicity in this architecture, we might pass the path to the CSV.
    # If we passed a dataframe in memory before, we now need to save it to temp csv.
    
    pipeline = PPLPipeline(args.data_path, output_dir=args.output_dir)
    
    # Clean/parse lists from args if passed as strings (or rely on simpler types)
    # Input/Output cols are usually lists. passing them via CLI is tricky if list.
    # Strategy: Pass a temp config yaml for training too? Or just JSON string.
    # Let's assume args.input_cols is a string "col1,col2"
    
    input_cols = [c.strip() for c in args.input_cols.split(',')] if args.input_cols else []
    output_cols = [c.strip() for c in args.output_cols.split(',')] if args.output_cols else []
    
    # Callback
    def pipeline_callback(msg, step, total):
        # Map pipeline steps (0-5) to our standardized output
        status_printer(msg, step, total)

    status_printer("Starting Training Pipeline...", 1, 5)
    
    results = pipeline.run(
        input_cols=input_cols,
        output_cols=output_cols,
        sample_size=args.sample_size,
        epochs=args.epochs,
        lime_samples=args.lime_samples,
        shap_samples=args.shap_samples,
        window_size=args.window_size,
        run_name=args.run_name,
        status_callback=pipeline_callback
    )
    
    # Save Results
    results_path = os.path.join(args.output_dir, "results.pkl")
    with open(results_path, "wb") as f:
        pickle.dump(results, f)
        
    status_printer("Process Complete", 5, 5)

def evaluate(args):
    status_printer("Initializing Worker...", 0, 5)
    
    # Dummy data path since we assume override or similar, 
    # BUT pipeline needs a path. We'll use the one passed or dummy.
    pipeline = PPLPipeline(data_path="dummy.csv", output_dir="output")
    
    # Load Data for override
    # If app passed a data path for evaluation data
    df_override = None
    if args.data_path and os.path.exists(args.data_path):
        df_override = pd.read_csv(args.data_path)
        # Apply filters if needed? 
        # For now assume data_path contains ready-to-use data (or pipeline cleans it)
    
    def pipeline_callback(msg, step, total):
        status_printer(msg, step, total)

    results = pipeline.evaluate_existing_model(
        model_path=args.model_path,
        config_path=args.config_path,
        df_override=df_override,
        lime_samples=args.lime_samples,
        shap_samples=args.shap_samples,
        status_callback=pipeline_callback
    )
    
    # Save Results (reuse output_dir logic, though result structure has 'output_dir' inside)
    # We need a place to save the pickle for the app to pick up.
    # Use output_dir arg.
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    results_path = os.path.join(args.output_dir, "results.pkl")
    with open(results_path, "wb") as f:
        pickle.dump(results, f)
        
    status_printer("Process Complete", 5, 5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    
    # Train Parser
    p_train = subparsers.add_parser("train")
    p_train.add_argument("--data_path", required=True)
    p_train.add_argument("--output_dir", required=True)
    p_train.add_argument("--input_cols", required=True, help="Comma-separated")
    p_train.add_argument("--output_cols", required=True, help="Comma-separated")
    p_train.add_argument("--sample_size", type=int, default=100)
    p_train.add_argument("--epochs", type=int, default=20)
    p_train.add_argument("--lime_samples", type=int, default=100)
    p_train.add_argument("--shap_samples", type=int, default=50)
    p_train.add_argument("--window_size", type=int, default=32)
    p_train.add_argument("--run_name", default="experiment")
    
    # Evaluate Parser
    p_eval = subparsers.add_parser("evaluate")
    p_eval.add_argument("--model_path", required=True)
    p_eval.add_argument("--config_path", required=True)
    p_eval.add_argument("--data_path", required=True) # Data to evaluate on
    p_eval.add_argument("--output_dir", required=True) # Where to save results.pkl
    p_eval.add_argument("--lime_samples", type=int, default=100)
    p_eval.add_argument("--shap_samples", type=int, default=50)

    args = parser.parse_args()
    
    # Safe guard for macOS fork safety if still relevant in subprocess, 
    # but since it's a fresh exec, it should be fine.
    # We can set env vars here just in case.
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    try:
        if args.mode == "train":
            train(args)
        elif args.mode == "evaluate":
            evaluate(args)
    except Exception as e:
        # Print error to stdout uniquely
        print(f"ERROR|{str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
