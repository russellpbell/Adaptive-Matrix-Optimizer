import pandas as pd
import matplotlib.pyplot as plt
import os

def explore_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Data Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head())
    
    # Plot first 4 variables
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(df.columns[:4]):
        plt.subplot(4, 1, i+1)
        plt.plot(df[col].iloc[:1000])
        plt.title(col)
        plt.grid(True)
    
    plt.tight_layout()
    output_plot = "data/exploration_plot.png"
    plt.savefig(output_plot)
    print(f"Saved exploration plot to {output_plot}")

if __name__ == "__main__":
    explore_data("data/python_data_1year.csv")
