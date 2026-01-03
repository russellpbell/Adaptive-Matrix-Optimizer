import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    # Cell 1: Imports and Setup
    text_1 = """\
# PPL Interactive Interface
This notebook allows you to explore the Tennessee Eastman Process dataset, define model inputs/outputs, train the pipeline, and visualize results.
"""
    code_1 = """\
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display, clear_output

# Add src to path
sys.path.append(os.path.abspath('..'))

from src.pipeline import PPLPipeline
from src.preprocessing import apply_savitzky_golay

%load_ext autoreload
%autoreload 2
%matplotlib inline
"""

    # Cell 2: Load Data
    code_2 = """\
data_path = '../data/python_data_1year.csv'
if not os.path.exists(data_path):
    print("Data file not found! Please run src/download_data.py first.")
else:
    df = pd.read_csv(data_path, sep=';')
    # Add timestamp if missing
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='3min')
    print(f"Loaded data: {df.shape}")
    display(df.head())
"""

    # Cell 3: Data Exploration Widget
    code_3 = """\
# Variable Selection for Plotting
variables = [c for c in df.columns if c != 'timestamp']
style = {'description_width': 'initial'}

plot_selector = widgets.SelectMultiple(
    options=variables,
    value=[variables[0]],
    description='Select Variables to Plot:',
    disabled=False,
    layout=widgets.Layout(width='50%', height='200px'),
    style=style
)

plot_output = widgets.Output()

def update_plot(change):
    with plot_output:
        clear_output(wait=True)
        selected = change['new']
        if not selected:
            return
        
        plt.figure(figsize=(15, 6))
        for col in selected:
            plt.plot(df['timestamp'][:1000], df[col][:1000], label=col) # Plot first 1000 for speed
        plt.legend()
        plt.title("Data Exploration (First 1000 points)")
        plt.grid(True)
        plt.show()

plot_selector.observe(update_plot, names='value')

display(widgets.VBox([widgets.Label("Select variables to overlay:"), plot_selector, plot_output]))
# Trigger initial plot
update_plot({'new': plot_selector.value})
"""

    # Cell 4: Model Configuration
    code_4 = """\
# Model Configuration
print("Configure Model Inputs (MVs/DVs) and Outputs (CVs)")

# Identify likely MVs, DVs, CVs based on naming convention
mvs = [c for c in variables if 'XMV' in c]
dvs = [c for c in variables if 'fault' in c or 'IDV' in c] # Adjust if DVs have specific names
cvs = [c for c in variables if 'XMEAS' in c]

# If no specific naming, just list all
if not mvs: mvs = variables
if not cvs: cvs = variables

input_selector = widgets.SelectMultiple(
    options=variables,
    value=mvs[:5] if mvs else variables[:5],
    description='Inputs (MVs/DVs):',
    layout=widgets.Layout(width='45%', height='200px'),
    style=style
)

output_selector = widgets.SelectMultiple(
    options=variables,
    value=cvs[:5] if cvs else variables[:5],
    description='Outputs (CVs):',
    layout=widgets.Layout(width='45%', height='200px'),
    style=style
)

display(widgets.HBox([input_selector, output_selector]))
"""

    # Cell 5: Train Model
    code_5 = """\
# Training Controls
train_button = widgets.Button(description="Train Model", button_style='success')
train_output = widgets.Output()

def on_train_click(b):
    with train_output:
        clear_output()
        print("Initializing Pipeline...")
        
        input_cols = list(input_selector.value)
        output_cols = list(output_selector.value)
        
        if not input_cols or not output_cols:
            print("Error: Please select at least one input and one output.")
            return
            
        print(f"Inputs: {len(input_cols)} variables")
        print(f"Outputs: {len(output_cols)} variables")
        
        pipeline = PPLPipeline(data_path, output_dir='../output')
        
        # Run pipeline
        # Using small sample size for interactive demo
        history, mse = pipeline.run(input_cols=input_cols, output_cols=output_cols, sample_size=200, epochs=5)
        
        print(f"Training Complete. Final MSE: {mse:.4f}")
        
        # Plot Loss
        plt.figure(figsize=(10, 4))
        plt.plot(history.history['loss'], label='Train Loss')
        if 'val_loss' in history.history:
            plt.plot(history.history['val_loss'], label='Val Loss')
        plt.title('Model Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()
        
        # Show generated artifacts
        print("Displaying generated visualizations...")
        try:
            from IPython.display import Image
            display(Image(filename='../output/error_dist.png'))
            display(Image(filename='../output/lime_violin.png'))
        except Exception as e:
            print(f"Could not display images: {e}")

train_button.on_click(on_train_click)
display(train_button, train_output)
"""

    nb['cells'] = [
        nbf.v4.new_markdown_cell(text_1),
        nbf.v4.new_code_cell(code_1),
        nbf.v4.new_code_cell(code_2),
        nbf.v4.new_code_cell(code_3),
        nbf.v4.new_code_cell(code_4),
        nbf.v4.new_code_cell(code_5)
    ]
    
    if not os.path.exists('notebooks'):
        os.makedirs('notebooks')
        
    with open('notebooks/PPL_Interactive_Interface.ipynb', 'w') as f:
        nbf.write(nb, f)
    
    print("Created notebooks/PPL_Interactive_Interface.ipynb")

if __name__ == "__main__":
    create_notebook()
