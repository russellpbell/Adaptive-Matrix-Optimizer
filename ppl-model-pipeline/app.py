import os

# Set environment variables for TensorFlow/Streamlit compatibility before importing other modules
# These must be set before ANY other imports to be effective
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress INFO and WARNING logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# Add src to path
sys.path.append(os.path.abspath('.'))
# from src.pipeline import PPLPipeline

def apply_bad_data_rules(df, rules):
    """
    Apply a list of bad data rules to a DataFrame.
    Rules can be value-based (remove if condition met) or time-based (remove if within period).
    Note: The logic retains data that does NOT match the 'Bad' condition.
    """
    if not rules:
        return df
        
    filtered_df = df.copy()
    for r in rules:
        r_type = r.get('type', 'value')
        
        if r_type == 'value':
            col = r['col']
            val = r['val']
            op = r['op']
            # We keep rows where the Bad Data Rule is FALSE
            # Rule: "Value > 10" is BAD -> Keep "Value <= 10"
            if op == ">": filtered_df = filtered_df[filtered_df[col] <= val]
            elif op == "<": filtered_df = filtered_df[filtered_df[col] >= val]
            elif op == "=": filtered_df = filtered_df[filtered_df[col] != val]
            elif op == ">=": filtered_df = filtered_df[filtered_df[col] < val]
            elif op == "<=": filtered_df = filtered_df[filtered_df[col] > val]
            elif op == "<>": filtered_df = filtered_df[filtered_df[col] == val] # Rule: != 10 is Bad -> Keep == 10
            
        elif r_type == 'time_exclude':
            start = pd.to_datetime(r['start'])
            end = pd.to_datetime(r['end'])
            if 'timestamp' in filtered_df.columns:
                # Exclude range [start, end]
                mask = (filtered_df['timestamp'] < start) | (filtered_df['timestamp'] > end)
                filtered_df = filtered_df[mask]
                
    return filtered_df


st.set_page_config(page_title="Adaptive Matrix Optimization", layout="wide")

# --- Authentication Bypass / Landing Page ---
if 'app_granted' not in st.session_state:
    st.session_state['app_granted'] = False

if not st.session_state['app_granted']:
    # --- Marketing / Login Page Content ---
    st.markdown("""
<style>
/* Card Container using Streamlit Theme Variables */
.landing-card {
    padding: 2rem; /* Reduced padding */
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Titles */
.landing-title {
    color: var(--text-color);
    font-family: 'Helvetica Neue', sans-serif;
    margin-bottom: 0.5rem;
}

.landing-subtitle {
     color: var(--text-color);
     opacity: 0.8;
     font-weight: 300;
     margin-bottom: 2rem;
}


/* Content Text */
.landing-content {
    text-align: left;
    padding: 0 1rem;
    color: var(--text-color);
}

.landing-content strong {
    color: var(--primary-color);
}

/* Center the Streamlit Button */
/* We target the container of the button. */
/* Using both flex and text-align for robustness */
div.stButton {
    display: flex;
    justify-content: center;
    width: 100%; 
    margin-top: 2rem;
}
div.stButton > button {
    display: inline-flex;
}
</style>

<div class="landing-card">
<h1 class="landing-title">Adaptive Matrix Optimization</h1>
<h3 class="landing-subtitle">Next-Generation Open-Loop Optimizer for Industrial Systems</h3>

<div class="landing-content">
<p style="font-size: 1.1rem; line-height: 1.5;">
<strong>Welcome to a future of predictable performance and aligned organizations.</strong>
</p>
<p>
Upload your timeseries data and our advanced modeling and optimization engine will unlock unprecedented insights and recommendations.
</p>
<ul style="line-height: 1.6; padding-left: 20px; margin-top: 1rem;">
<li><strong>Machine Learning Modeling:</strong> Understand your process based on your data rather than a theoretical simulation.</li>
<li><strong>Data Privacy:</strong> We never store your data and we allow you to download all of the insights and models created based on your data. Data is processed locally.</li>
<li><strong>What-If & Real Time Optimization:</strong> Use our unique pipeline for optimizing processes to unlock more value from your processes.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)

    # Render button using columns for centering
    # Use ratios to push button to absolute center without making it full width
    col1, col2, col3 = st.columns([5, 2, 5])
    with col2:
        if st.button("Continue to App", type="primary"):
            st.session_state['app_granted'] = True
            st.rerun()

    # Create space effectively pushing footer down if needed
    st.write("")
    
    # Stop execution here so the rest of the app doesn't run until granted
    st.stop()


# try:
#     from st_paywall import add_auth
#     import st_paywall.aggregate_auth
#     import st_paywall.stripe_auth
# 
#     # Monkey-patch to whitelist admin email
#     # We use stripe_auth as the source of truth for the original function
#     original_is_active_subscriber = st_paywall.stripe_auth.is_active_subscriber
# 
#     def monkey_patched_is_active_subscriber(email):
#         if email in ["russellpaulbell@gmail.com", "danieljdurr@gmail.com"]:
#             return True
#         return original_is_active_subscriber(email)
# 
#     # Patch both locations to ensure the redirect uses our logic
#     st_paywall.stripe_auth.is_active_subscriber = monkey_patched_is_active_subscriber
#     st_paywall.aggregate_auth.is_active_subscriber = monkey_patched_is_active_subscriber
# 
#     # --- DEBUG: Show the exact URL being used for Auth ---
#     # This helps debug the "redirect_uri_mismatch" error
#     if "redirect_url" in st.secrets:
#         st.info(f"**Debug Info:** The app is configured to redirect to: `{st.secrets['redirect_url']}`")
#         st.caption("Please copy this EXACT URL and paste it into 'Authorized redirect URIs' in your Google Cloud Console.")
# 
# except KeyError as e:
#     st.error("🚨 **Missing Secrets Configuration!** 🚨")
#     st.markdown(f"""
#     The application failed to load because a required secret is missing: `{e}`.
#     
#     **How to fix this on Streamlit Cloud:**
#     1. Go to your App Dashboard on Streamlit Cloud.
#     2. Click **Settings** (three dots) -> **Settings** -> **Secrets**.
#     3. Paste your valid `secrets.toml` content (Google Client ID, Stripe Keys, etc.).
#     4. Reboot the app.
#     """)
#     st.stop()
# except Exception as e:
#     st.error(f"An unexpected error occurred during authentication setup: {e}")
#     st.stop()
# 
# # --- Marketing / Login Page Content ---
# intro_text = st.empty()
# intro_text.markdown("""
# <div style="padding: 3rem 2rem; max-width: 900px; margin: 0 auto; text-align: center; color: #e0e0e0; background-color: #1e1e1e; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
#     <h1 style="color: #ffffff; font-family: 'Helvetica Neue', sans-serif;">Adaptive Matrix Optimization</h1>
#     <h3 style="color: #a0a0a0; font-weight: 300;">Next-Generation Open-Loop Optimizer for Industrial Systems</h3>
#     <br>
#     <div style="padding: 20px; text-align: left;">
#         <p style="font-size: 1.1rem; line-height: 1.6; color: #f0f0f0;">
#             <strong>Welcome to a future of predictable performance and aligned organizations.</strong>
#         </p>
#         <p style="color: #cccccc;">
#             Upload your timeseries data and our advanced modeling and optimization engine will unlock unprecedented insights and recommendations.
#         </p>
#         <ul style="margin-top: 20px; margin-bottom: 30px; color: #cccccc; line-height: 1.8;">
#             <li><strong style="color: #fff;">Machine Learning Modeling:</strong> Understand your process based on your data rather than a theoretical simulation.</li>
#             <li><strong style="color: #fff;">Data Privacy:</strong> We never store your data and we allow you to download all of the insights and models created based on your data. Data is processed locally, so we couldn't see it even if we wanted to.</li>
#             <li><strong style="color: #fff;">What-If & Real Time Optimization:</strong> Use our unique pipeline for optimizing processes to unlock more value from your processes.</li>
#         </ul>
#         <p style="font-size: 0.9rem; color: #888; text-align: center; margin-top: 20px; border-top: 1px solid #444; padding-top: 20px;">
#             Please login via the sidebar to access the application.
#         </p>
#     </div>
# </div>
# """, unsafe_allow_html=True)
# 
# add_auth(
#     required=True,
#     login_button_text="Login with Google",
#     login_button_color="#FD504D",
#     login_sidebar=True,
# )
# 
# # Clear marketing text after login
# intro_text.empty()

st.markdown("<h1 style='text-align: center;'>Adaptive Matrix Optimization</h1>", unsafe_allow_html=True)

# Navigation
# Navigation State
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Exploration", "Model Training / Exploration", "Optimization"])
st.session_state['current_page'] = page

# --- PAGE 1: Data Exploration ---
if st.session_state['current_page'] == "Data Exploration":
    st.header("Data Exploration")
    
    import plotly.express as px
    
    # Shared Data Loading
    if 'shared_df' not in st.session_state:
        st.info("Please upload data to begin exploration.")
        uploaded_file = st.file_uploader("Upload CSV Data", type=['csv'], key="eda_uploader")
        if uploaded_file and 'shared_df' not in st.session_state:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
            except:
                df = pd.read_csv(uploaded_file)
            
            cols_lower = [c.lower() for c in df.columns]
            if 'timestamp' in cols_lower:
                ts_col = df.columns[cols_lower.index('timestamp')]
                df.rename(columns={ts_col: 'timestamp'}, inplace=True)
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df.dropna(subset=['timestamp'], inplace=True)
            else:
                st.warning("No 'timestamp' column found. Index will be used.")
                df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='1H')
            
            st.session_state['shared_df'] = df
            st.rerun()

    # Always show uploader in expander if data exists
    if 'shared_df' in st.session_state:
        with st.expander("Change Dataset", expanded=False):
             new_file = st.file_uploader("Upload New CSV Data", type=['csv'], key="eda_uploader_change")
             if new_file: 
                 try:
                     df_new = pd.read_csv(new_file, sep=None, engine='python')
                 except:
                     df_new = pd.read_csv(new_file)
                 
                 cols_lower = [c.lower() for c in df_new.columns]
                 if 'timestamp' in cols_lower:
                     ts_col = df_new.columns[cols_lower.index('timestamp')]
                     df_new.rename(columns={ts_col: 'timestamp'}, inplace=True)
                     df_new['timestamp'] = pd.to_datetime(df_new['timestamp'], errors='coerce')
                     df_new.dropna(subset=['timestamp'], inplace=True)
                 else:
                     st.warning("No 'timestamp' column found. Index will be used.")
                     df_new['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df_new), freq='1H')
                 
                 st.session_state['shared_df'] = df_new
                 st.session_state['bad_data_rules'] = [] # Reset rules on new data
                 st.rerun()
    
    if 'shared_df' in st.session_state:
        df = st.session_state['shared_df']
        
        if 'timestamp' in df.columns:
             if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                 df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
             df.dropna(subset=['timestamp'], inplace=True)
        
        # --- EDA Content ---
        st.markdown("### Bad Data Rules (Filter)")
        all_cols = [c for c in df.columns if c != 'timestamp']
        
        if 'bad_data_rules' not in st.session_state:
            st.session_state['bad_data_rules'] = []
        
        # Rule Type Selection (Outside Form for interactivity)
        rule_type = st.selectbox("Rule Type", ["Value Threshold", "Time Period Exclusion"], key="rule_type_selector")

        with st.form("add_rule"):
            if rule_type == "Value Threshold":
                c1, c2, c3 = st.columns(3)
                rule_col = c1.selectbox("Column", all_cols)
                rule_op = c2.selectbox("Operator (Identify Bad Data)", [">", "<", "=", ">=", "<=", "<>"]) 
                rule_val = c3.number_input("Value", value=0.0)
                
                if st.form_submit_button("Add Rule"):
                    st.session_state['bad_data_rules'].append({
                        'type': 'value', 
                        'col': rule_col, 
                        'op': rule_op, 
                        'val': rule_val
                    })
                    st.rerun()
            else:
                # Time Period
                c1, c2 = st.columns(2)
                # Default defaults
                def_start = df['timestamp'].min() if 'timestamp' in df.columns else pd.Timestamp.now()
                def_end = df['timestamp'].max() if 'timestamp' in df.columns else pd.Timestamp.now()
                
                t_start = c1.date_input("Start Date", value=def_start)
                t_end = c2.date_input("End Date", value=def_end)
                
                if st.form_submit_button("Add Rule"):
                    st.session_state['bad_data_rules'].append({
                        'type': 'time_exclude',
                        'start': str(t_start),
                        'end': str(t_end)
                    })
                    st.rerun()

        if st.session_state['bad_data_rules']:
            st.markdown("**Active Rules:**")
            for i, r in enumerate(st.session_state['bad_data_rules']):
                c1, c2 = st.columns([4, 1])
                r_type = r.get('type', 'value')
                if r_type == 'value':
                    c1.text(f"Exclude if {r['col']} {r['op']} {r['val']}")
                elif r_type == 'time_exclude':
                    c1.text(f"Exclude {r['start']} to {r['end']}")
                else:
                    c1.text(f"Unknown rule: {r}")
                if c2.button("X", key=f"del_rule_{i}"):
                    del st.session_state['bad_data_rules'][i]
                    st.rerun()
        
        filtered_df = apply_bad_data_rules(df, st.session_state['bad_data_rules'])
        
        st.markdown(f"**Data after filtering:** {len(filtered_df)} / {len(df)}")
        
        st.markdown("### Date Range")
        min_date = df['timestamp'].min().to_pydatetime()
        max_date = df['timestamp'].max().to_pydatetime()
        
        date_range = st.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="MM/DD/YY")
        start_d, end_d = date_range
        
        date_mask = (df['timestamp'] >= pd.to_datetime(start_d)) & (df['timestamp'] <= pd.to_datetime(end_d))
        base_view_df = df.loc[date_mask]
        
        good_view_df = apply_bad_data_rules(base_view_df, st.session_state['bad_data_rules'])

        st.markdown("### Timeseries")
        st.markdown("#### Select variables to plot")
        selected_vars = st.multiselect("Variables", all_cols, default=[])

        if selected_vars:
            # Define color sequence/map for consistency
            # Plotly default sequence
            default_colors = px.colors.qualitative.Plotly
            var_color_map = {var: default_colors[i % len(default_colors)] for i, var in enumerate(selected_vars)}

            # Melt for faceting
            melted_df = base_view_df.melt(id_vars='timestamp', value_vars=selected_vars, var_name='Variable', value_name='Value')
            
            # Faceted layout with independent Y axes and distinct colors
            fig = px.line(melted_df, x='timestamp', y='Value', color='Variable', color_discrete_map=var_color_map, facet_row='Variable', title="Variable Trends (Autoscaled)", height=300 * len(selected_vars))
            fig.update_yaxes(matches=None, showticklabels=True) # Independent scaling
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])) # Clean labels
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### Distributions")
            st.markdown("Distribution of selected variables.")
            
            # Grid of histograms for selected variables
            cols_per_row = 3
            for i in range(0, len(selected_vars), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(selected_vars):
                        var = selected_vars[i+j]
                        with cols[j]:
                            # Apply matching color
                            color = var_color_map[var]
                            fig_hist = px.histogram(good_view_df, x=var, nbins=50, title=f"{var}", height=250, color_discrete_sequence=[color])
                            fig_hist.update_layout(margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
                            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Select variables above to see plots.")

    st.divider()
    # Removed Navigation Buttons (Sidebar Used)

# --- PAGE 2: Model Training ---
elif st.session_state['current_page'] == "Model Training / Exploration":
    st.header("Model Training Pipeline")
    
    # Lazy import to prevent freezing/locking on startup
    from src.pipeline import PPLPipeline
    
    st.subheader("Data Loading")
    
    # Initialize variables to avoid NameError
    uploaded_file = None
    selected_file = None
    data_dir = 'data'
    
    if 'shared_df' in st.session_state:
        st.info("Using data loaded in Data Exploration.")
        df = st.session_state['shared_df']
        st.write(f"Data Shape: {df.shape}")
    else:
        uploaded_file = st.file_uploader("Upload CSV Data (if not loaded)", type=['csv'])
        df = None
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
            except:
                df = pd.read_csv(uploaded_file)
            
            cols_lower = [c.lower() for c in df.columns]
            if 'timestamp' in cols_lower:
                ts_col = df.columns[cols_lower.index('timestamp')]
                df.rename(columns={ts_col: 'timestamp'}, inplace=True)
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df.dropna(subset=['timestamp'], inplace=True)
            else:
                 st.warning("No 'timestamp' column found. Index will be used.")
                 df['timestamp'] = pd.date_range(start='2023-01-01', periods=len(df), freq='1H')
            
            st.session_state['shared_df'] = df
            st.success(f"Loaded data: {df.shape}")
        else:
            data_dir = 'data'
            if os.path.exists(data_dir):
                 csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                 if csv_files:
                     use_sample = st.checkbox("Use Sample Data", value=False)
                     if use_sample:
                         selected_file = st.selectbox("Select Sample File", csv_files)
                         df = pd.read_csv(os.path.join(data_dir, selected_file), sep=None, engine='python')
                         if 'timestamp' in df.columns: 
                             df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                         st.session_state['shared_df'] = df

    if df is not None:
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp'], inplace=True)
            
        all_cols = [c for c in df.columns if c != 'timestamp']
        
        filtered_df = df.copy()
        if 'bad_data_rules' in st.session_state:
             filtered_df = apply_bad_data_rules(filtered_df, st.session_state['bad_data_rules'])
        
        st.write(f"Training on {len(filtered_df)} samples (after filters).")
                
        # 3. Training / Loading Configuration
        # Create tabs for Training vs Loading
        tab_train, tab_load = st.tabs(["Train New Model", "Load Existing Model"])
        
        with tab_train:
            st.subheader("Train New Model")
            col1, col2 = st.columns(2)
            with col1:
                input_cols = st.multiselect("Input Features (MVs/DVs)", all_cols, default=[])
            with col2:
                output_cols = st.multiselect("Output Targets (CVs)", all_cols, default=[])
                
            # Quality Presets Logic
            N_samples = len(filtered_df)
            
            if 'quality_selector' not in st.session_state:
                st.session_state['quality_selector'] = "Quick"
                # Init defaults
                st.session_state['epochs_in'] = 20
                st.session_state['samples_in'] = min(1000, N_samples)
                st.session_state['interp_in'] = 500 # Unified Interpretation samples (LIME=Val, SHAP=Val/2)
    
            def calculate_stat_sample(N, confidence=0.99, margin_of_error=0.03):
                target = 1844
                return min(target, N)
    
            def on_quality_change():
                q = st.session_state['quality_selector']
                N = len(filtered_df) 
                stat_n = calculate_stat_sample(N) # Target ~1850
                
                if q == 'Quick':
                    st.session_state['epochs_in'] = 20
                    st.session_state['samples_in'] = min(1000, N)
                    st.session_state['interp_in'] = stat_n 
                elif q == 'Balanced':
                    st.session_state['epochs_in'] = 100
                    st.session_state['samples_in'] = min(5000, N)
                    st.session_state['interp_in'] = stat_n
                elif q == 'Deep Training':
                    st.session_state['epochs_in'] = 500
                    st.session_state['samples_in'] = N
                    st.session_state['interp_in'] = stat_n
    
            # 1. Process Residence Time (Full Row, Above)
            st.caption("Process Dynamics Parameter")
            window_size = st.number_input("Process Residence Time (Window Size)", min_value=10, max_value=200, value=32, key="window_size_in", help="Number of past time steps the model looks back to make a prediction.")
    
            # 2. Training Quality & Run Name (Columns)
            c_qual, c_name = st.columns([0.5, 0.5])
            with c_qual:
                st.radio("Training Quality", ["Quick", "Balanced", "Deep Training"], key="quality_selector", on_change=on_quality_change, horizontal=True)
                
            with c_name:
                 run_name = st.text_input("Run Name (Experiment ID)", value="experiment_v1")
            
        # Advanced Settings below...
        with tab_train:
            with st.expander("Advanced Settings (Epochs, Samples, Interpretation)", expanded=False):
                ac1, ac2 = st.columns(2)
                epochs = ac1.number_input("Epochs", min_value=1, value=st.session_state.get('epochs_in', 20), key="epochs_in")
                sample_size = ac2.number_input("Training Sample Size", min_value=10, max_value=len(filtered_df), value=st.session_state.get('samples_in', 100), key="samples_in")
                
                # Unified Interpretability Input
                rec_n = calculate_stat_sample(N_samples)
                interp_samples = st.number_input(f"Model Interpretability Samples (99% Conf: ~{rec_n})", min_value=10, value=st.session_state.get('interp_in', rec_n), key="interp_in", help="Combined sample size for LIME and SHAP analysis.")
                
            # UI for Folder Picker
            output_parent_dir = "../output"
            resolved_parent = os.path.abspath(output_parent_dir)
            if not os.path.exists(resolved_parent):
                os.makedirs(resolved_parent, exist_ok=True)
                
            st.write("**Output Directory**")
            st.info(f"Artifacts will be saved to: `../output/{run_name}`")
            final_output_path = os.path.join(resolved_parent, run_name)
    
            # Helper for running subprocess
            def run_worker_process(command, progress_placeholder):
                import subprocess
                import sys
                import pickle
                
                # Reset Progress
                def update_ui(pipeline_step, msg):
                    # Map Pipeline Steps (1-6) to UI Phases (0-4)
                    # Pipeline: 1=Load, 2=Preproc, 3=Encode, 4=Model, 5=Train, 6=Interp
                    # UI: 0=Init, 1=Preproc, 2=Model Ops, 3=Explanations, 4=Complete
                    
                    ui_phase = 0
                    if pipeline_step == 1: ui_phase = 0 # Initializing
                    elif pipeline_step in [2, 3]: ui_phase = 1 # Preprocessing
                    elif pipeline_step in [4, 5]: ui_phase = 2 # Model Operations
                    elif pipeline_step == 6: ui_phase = 3 # Explanations
                    elif pipeline_step > 6: ui_phase = 4 # Complete
                    
                    steps = [
                         ("Initializing...", "done" if ui_phase > 0 else "running"),
                         ("Preprocessing Data...", "done" if ui_phase > 1 else ("running" if ui_phase == 1 else "wait")),
                         ("Model Operations...", "done" if ui_phase > 2 else ("running" if ui_phase == 2 else "wait")),
                         ("Generating Explanations...", "done" if ui_phase > 3 else ("running" if ui_phase == 3 else "wait")),
                         ("Complete", "done" if ui_phase > 4 else "wait")
                    ]
                    
                    md_str = "**Job Progress:**\n\n"
                    for i, (name, status) in enumerate(steps):
                         icon = "✅" if status == "done" else ("⏳" if status == "running" else "⬜")
                         style = "font-weight: bold;" if status == "running" else ""
                         # Add message details if running
                         details = f" - *{msg}*" if status == "running" else ""
                         md_str += f"* {icon} <span style='{style}'>{name}</span>{details}\n"
                    progress_placeholder.markdown(md_str, unsafe_allow_html=True)

                # Prepare Environment with CPU enforcement
                worker_env = os.environ.copy()
                worker_env['CUDA_VISIBLE_DEVICES'] = '-1'
                worker_env['TF_ENABLE_ONEDNN_OPTS'] = '0'

                process = subprocess.Popen(
                    command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env=worker_env
                )
                
                error_lines = []
                
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    
                    if line:
                        stripped = line.strip()
                        if stripped.startswith("STATUS|"):
                            # Parse: STATUS|step|total|msg
                            parts = stripped.split('|')
                            if len(parts) >= 4:
                                step = int(parts[1])
                                msg = parts[3]
                                update_ui(step, msg)
                        elif stripped.startswith("ERROR|"):
                            st.error(f"Worker Error: {stripped[6:]}")
                        else:
                            print(f"[WORKER] {stripped}") # Debug to console
                
                # Check return code
                if process.returncode != 0:
                    err = process.stderr.read()
                    st.error(f"Worker Process Failed.\n{err}")
                    return None
                    
                return True

            # Resolve runner path absolute
            runner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'runner.py')

            if st.button("Start Training"):
                if not input_cols or not output_cols:
                    st.error("Please select at least one input and one output.")
                else:
                    progress_placeholder = st.empty()
                    
                    try:
                        # 1. Save Temp Data
                        # Resolve temp path relative to output
                        # Assuming output_parent_dir is defined
                        temp_data_path = os.path.abspath(os.path.join("../output", "temp_train_data.csv"))
                        resolved_out_dir = os.path.abspath("../output")
                        if not os.path.exists(resolved_out_dir): os.makedirs(resolved_out_dir)
                        
                        filtered_df.to_csv(temp_data_path, index=False)
                        
                        # 2. Construct Command
                        cmd = [
                            sys.executable, runner_path, "train",
                            "--data_path", temp_data_path,
                            "--output_dir", os.path.abspath(final_output_path),
                            "--input_cols", ",".join(input_cols),
                            "--output_cols", ",".join(output_cols),
                            "--sample_size", str(sample_size),
                            "--epochs", str(epochs),
                            "--lime_samples", str(interp_samples),
                            "--shap_samples", str(int(interp_samples//2)),
                            "--window_size", str(window_size),
                            "--run_name", run_name
                        ]
                        
                        st.info(f"Launching worker process...")
                        success = run_worker_process(cmd, progress_placeholder)
                        
                        if success:
                            # Load Results
                            res_pkl = os.path.join(final_output_path, "results.pkl")
                            if os.path.exists(res_pkl):
                                with open(res_pkl, "rb") as f:
                                    import pickle
                                    results = pickle.load(f)
                                    
                                st.success(f"Training Finished. Final MSE: {results['mse']:.5f}")
                                st.session_state['training_results'] = {
                                    'results': results,
                                    'run_name': run_name,
                                    'output_cols': output_cols
                                }
                            else:
                                st.error("Worker finished but no results.pkl found.")

                    except Exception as e:
                        st.error(f"Training Launch Failed: {e}")
                        import traceback
                        st.write(traceback.format_exc())

        with tab_load:
            st.write("### Upload Existing Model")
            st.write("Upload a previously trained model artifact (ZIP).")
            
            model_path_load = None
            config_path_load = None
            results_path_load = None
            
            if True: # Enforce ZIP format
                uploaded_zip = st.file_uploader("Model ZIP", type=['zip'])
                if uploaded_zip:
                    import zipfile
                    import shutil
                    temp_dir = "temp_load_model_zip"
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir)
                    
                    try:
                        # Extract the ZIP
                        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # Find config, model, and results
                        # Find config, model, and results
                        potential_configs = [os.path.join(dp, f) for dp, dn, filenames in os.walk(temp_dir) for f in filenames if f == 'config.yaml']
                        potential_models = [os.path.join(dp, f) for dp, dn, filenames in os.walk(temp_dir) for f in filenames if f.endswith('.keras') or f.endswith('.h5')]
                        potential_results = [os.path.join(dp, f) for dp, dn, filenames in os.walk(temp_dir) for f in filenames if f == 'results.pkl']
                        
                        if potential_configs and potential_models:
                            config_path_load = potential_configs[0]
                            model_path_load = potential_models[0]
                            
                            msg = f"Found config: {os.path.basename(config_path_load)} and model: {os.path.basename(model_path_load)}"
                            if potential_results:
                                results_path_load = potential_results[0]
                                msg += f" and pre-calculated results: {os.path.basename(results_path_load)}"
                            else:
                                results_path_load = None
                                
                            st.success(msg)
                        else:
                            st.error("Could not find 'config.yaml' and a '.keras/.h5' model file in the ZIP.")
                    except Exception as e:
                        st.error(f"Error processing ZIP: {e}")
                        
            # Individual files upload removed.

            if st.button("Load and Evaluate Model"):
                if model_path_load and config_path_load:
                    try:
                        progress_placeholder = st.empty()
                        
                        # FAST PATH: Open existing results if available
                        if results_path_load and os.path.exists(results_path_load):
                            st.info("Loading pre-calculated results from artifact... (Skipping re-evaluation)")
                            with open(results_path_load, "rb") as f:
                                import pickle
                                results = pickle.load(f)
                            
                            st.success("Loaded Results Successfully!")
                            output_cols_loaded = results['config']['output_columns']
                            run_name_loaded = results['config']['run_name']
                            
                            st.session_state['training_results'] = {
                                'results': results,
                                'run_name': run_name_loaded,
                                'output_cols': output_cols_loaded
                            }
                            st.rerun()
                            
                        else:
                            # SLOW PATH: Run evaluation worker
                            # 1. Save Temp Data for Evaluation
                            # We use filtered_df from app
                            # Ensure absolute path resolution for temp files
                            temp_data_path = os.path.abspath(os.path.join("../output", "temp_eval_data.csv"))
                            
                            # 2. Output Dir (Temp for loading)
                            temp_out_dir = os.path.abspath(os.path.join("../output", "temp_eval_results"))
                            
                            # 3. Construct Command
                            cmd = [
                                sys.executable, runner_path, "evaluate",
                                "--model_path", os.path.abspath(model_path_load),
                                "--config_path", os.path.abspath(config_path_load),
                                "--data_path", temp_data_path,
                                "--output_dir", temp_out_dir,
                                "--lime_samples", "50",
                                "--shap_samples", "25"
                            ]
                            
                            st.info("No pre-calculated results found. Launching isolated evaluation process...")
                            success = run_worker_process(cmd, progress_placeholder)
                            
                            if success:
                                # Load Results
                                res_pkl = os.path.join(temp_out_dir, "results.pkl")
                                if os.path.exists(res_pkl):
                                    with open(res_pkl, "rb") as f:
                                        import pickle
                                        results = pickle.load(f)
                                    
                                    st.success("Evaluation / Loading Complete!")
                                    
                                    output_cols_loaded = results['config']['output_columns']
                                    run_name_loaded = results['config']['run_name']
                                    
                                    st.session_state['training_results'] = {
                                        'results': results,
                                        'run_name': run_name_loaded,
                                        'output_cols': output_cols_loaded
                                    }
                                    st.rerun()
                                else:
                                    st.error("Worker finished but no results.pkl found.")
                        
                    except Exception as e:
                        st.error(f"Failed to load/evaluate model: {e}")
                        import traceback
                        st.write(traceback.format_exc())
                else:
                    st.warning("Please upload files to proceed.")
                    
        # Check for results in Session State
        if 'training_results' in st.session_state:
            res_data = st.session_state['training_results']
            results = res_data['results']
            run_name = res_data['run_name']
            output_cols = res_data['output_cols']

            # --- Results Visualization ---
            st.subheader("Training Results")
            
            st.markdown("### Model Analysis")
            tab_scenario, tab_error, tab_relationships = st.tabs(["Scenario Explorer", "Error Analysis", "Model Relationships"])

            # --- Tab 1: Scenario Explorer ---
            with tab_scenario:
                # --- Scenario Filtering Logic ---
                st.markdown("**Random Scenario Explorer & Filters**")
                
                # Cache aggregated metrics if not present
                if 'scenario_metrics' not in st.session_state or st.session_state.get('last_run_name') != run_name:
                    with st.spinner("Calculating scenario metrics for filtering..."):
                        # Get data
                        y_true = results['y_true']
                        y_pred = results['y_pred']
                        X = results.get('X_windows') # (N, T, n_in)
                        
                        # Calculate Sample-wise Metrics
                        # 1. Error (MAE per sample)
                        errors = np.mean(np.abs(y_true - y_pred), axis=(1, 2))
                        
                        # 2. Input Means (per window, per feature)
                        # We need names.
                        input_names = results['config']['input_columns']
                        output_names = results['config']['output_columns']
                        
                        metrics_data = {'MAE': errors}
                        
                        # Add Mean Input Values
                        if X is not None:
                             # Mean over T dimension -> (N, n_in)
                             mean_inputs = np.mean(X, axis=1)
                             for i, name in enumerate(input_names):
                                 metrics_data[f"Input_Mean_{name}"] = mean_inputs[:, i]
                                 
                        # Add Mean Output Values (Actual)
                        mean_outputs = np.mean(y_true, axis=1)
                        for i, name in enumerate(output_names):
                             metrics_data[f"Output_Mean_{name}"] = mean_outputs[:, i]
                             
                        st.session_state['scenario_metrics'] = pd.DataFrame(metrics_data)
                        st.session_state['last_run_name'] = run_name
                
                metrics_df = st.session_state['scenario_metrics']
                
                # Filter UI
                if 'scenario_filters' not in st.session_state:
                     st.session_state['scenario_filters'] = []
                     
                with st.expander("Scenario Filters", expanded=True):
                    # Add Filter Form
                    c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
                    f_col = c1.selectbox("Metric", metrics_df.columns, key="filt_col")
                    f_op = c2.selectbox("Op", [">", "<"], key="filt_op")
                    f_val = c3.number_input("Value", value=0.0, key="filt_val")
                    if c4.button("Add"):
                        st.session_state['scenario_filters'].append({'col': f_col, 'op': f_op, 'val': f_val})
                        st.rerun()
                        
                    # Active Filters
                    if st.session_state['scenario_filters']:
                        st.markdown("**Active:**")
                        for i, f in enumerate(st.session_state['scenario_filters']):
                             st.text(f"{f['col']} {f['op']} {f['val']}")
                             if st.button("Remove", key=f"rm_filt_{i}"):
                                 del st.session_state['scenario_filters'][i]
                                 st.rerun()

                # Apply Filters to get valid indices
                valid_indices = metrics_df.index.tolist() # Start with all
                for f in st.session_state['scenario_filters']:
                    col = f['col']; op = f['op']; val = f['val']
                    if op == ">": valid_indices = metrics_df[metrics_df[col] > val].index.intersection(valid_indices)
                    elif op == "<": valid_indices = metrics_df[metrics_df[col] < val].index.intersection(valid_indices)
                
                pool_size = len(valid_indices)
                st.caption(f"Valid Scenarios Pool: {pool_size} / {len(metrics_df)}")
                
                if st.button("Pick Random Sample"):
                    if pool_size > 0:
                        import random
                        # Convert Index object to list for random.choice if needed, but safe to cast
                        idx_choice = np.random.choice(list(valid_indices))
                        st.session_state['rnd_sample_idx'] = int(idx_choice)
                    else:
                        st.warning("No scenarios match filters!")
                    
                if 'rnd_sample_idx' in st.session_state:
                    idx = st.session_state['rnd_sample_idx']
                    st.write(f"Analyzing Scenario **#{idx}**")
                    
                    X_wins = results.get('X_windows')
                    y_true_all = results['y_true']
                    y_pred_all = results['y_pred']
                    input_names = results['config']['input_columns']
                    output_names = results['config']['output_columns']
                    
                    st.markdown("### INPUTS")
                    if X_wins is not None:
                        current_x = X_wins[idx]
                        n_in = len(input_names)
                        cols = st.columns(n_in)
                        for i, col_name in enumerate(input_names):
                            series = current_x[:, i]
                            fig_in = px.line(y=series, title=col_name)
                            fig_in.update_traces(line_color='green')
                            fig_in.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), height=200)
                            cols[i].plotly_chart(fig_in, use_container_width=True)
                    
                    st.markdown("### OUTPUTS")
                    n_out = len(output_names)
                    cols_out = st.columns(n_out)
                    current_y_true = y_true_all[idx]
                    current_y_pred = y_pred_all[idx]
                    
                    for i, col_name in enumerate(output_names):
                        y_t = current_y_true[:, i]
                        y_p = current_y_pred[:, i]
                        df_p = pd.DataFrame({'Step': np.arange(len(y_t)), 'Actual': y_t, 'Predicted': y_p})
                        fig_out = px.line(df_p, x='Step', y=['Actual', 'Predicted'], title=col_name)
                        fig_out.update_traces(line_color='blue', selector=dict(name='Actual'))
                        fig_out.update_traces(line_color='red', line_dash='dash', selector=dict(name='Predicted'))
                        fig_out.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=200, legend=dict(orientation="h", y=-0.2))
                        cols_out[i].plotly_chart(fig_out, use_container_width=True)



            # --- Tab 3: Error Analysis ---
            with tab_error:
                st.markdown("#### Prediction Error Distribution")
                y_true = results['y_true']
                y_pred = results['y_pred']
                error = y_true - y_pred # (N, T, n_out)
                
                # Context Data (Samples)
                ctx_data = results['context_data']
                if ctx_data:
                    ctx_df = pd.DataFrame(ctx_data)
                    
                    # Construct detailed Error DataFrame for Linking
                    # Shape: (N, T, n_out)
                    N, T, n_out = error.shape
                    
                    # Create indices
                    sample_ids = np.repeat(np.arange(N), T * n_out) # Repeat for each timestep AND output? No.
                    # Flattening order: likely (N, T, n_out) -> Iterate N, then T, then Output?
                    # default C-style: last axis fast. output changes fastest.
                    # error.flatten(): Sample 0, T0, O0; Sample 0, T0, O1...
                    # So sample_id repeats (T * n_out) times.
                    sample_ids = np.repeat(np.arange(N), T * n_out)
                    
                    # Output names
                    # Tile output names: O0, O1, O2... repeated N*T times.
                    out_names_tile = np.tile(output_cols, N * T)
                    
                    # Flatten Error
                    flat_err = error.flatten()
                    
                    err_df = pd.DataFrame({
                        'Error': flat_err,
                        'Output': out_names_tile, 
                        'Sample_ID': sample_ids
                    })
                    
                    # --- Interactive Error Histogram ---
                    # We use a custom color column to enable highlighting if "self-selected" 
                    # ... but actually we just want to select FROM here.
                    
                    fig_err = px.histogram(err_df, x='Error', color='Output', barmode='overlay', 
                                         title="Global Prediction Error Distribution (Select range to filter)",
                                         nbins=100)
                    fig_err.update_layout(dragmode='select', hovermode='closest')
                    
                    # Display Chart & Capture Selection
                    selection = st.plotly_chart(fig_err, use_container_width=True, on_select="rerun", selection_mode=["box", "lasso"])
                    
                    # Logic to identify selected samples
                    selected_sample_ids = set()
                    
                    if selection and 'selection' in selection:
                         points = selection['selection'].get('points', [])
                         if points:
                             indices = []
                             for p in points:
                                 if 'point_indices' in p:
                                     indices.extend(p['point_indices'])
                                 elif 'point_index' in p:
                                     indices.append(p['point_index'])
                             
                             if indices:
                                 selected_sample_ids = set(err_df.iloc[indices]['Sample_ID'].unique())
                    
                    # Apply Selection to Context Data
                    if selected_sample_ids:
                        ctx_df['Segment'] = np.where(ctx_df['Sample_ID'].isin(selected_sample_ids), 'Selected', 'Other')
                        st.markdown(f"**Selected Samples:** {len(selected_sample_ids)} / {N}")
                    else:
                        ctx_df['Segment'] = 'Other' 
                        st.markdown(f"**Selected Samples:** 0 / {N} (Showing all)")

                    # Color map for consistency
                    color_map = {'Selected': 'red', 'Other': 'lightgray'}
                    
                    # --- Distributions Grid ---
                    st.divider()
                    
                    # Helper for Grid Plotting
                    def plot_grid(features, title_prefix):
                         st.markdown(f"### {title_prefix}")
                         if not features: 
                             return
                         
                         cols_per_row = 4
                         # Break into chunks
                         for i in range(0, len(features), cols_per_row):
                             cols = st.columns(cols_per_row)
                             for j in range(cols_per_row):
                                 if i + j < len(features):
                                     f_name = features[i+j]
                                     with cols[j]:
                                         # If we have selection, we show 'Selected' on top?
                                         # barmode='overlay' handles it.
                                         # If Segment column is uniform (all 'Other'), it just shows gray.
                                         
                                         # Check if we have data for this feature
                                         if f_name in ctx_df.columns:
                                             fig = px.histogram(ctx_df, x=f_name, color='Segment', 
                                                              color_discrete_map=color_map,
                                                              barmode='overlay',
                                                              title=f_name,
                                                              height=200)
                                             fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
                                             st.plotly_chart(fig, use_container_width=True)
                                         else:
                                             # For Targets, maybe we need to compute/fetch them?
                                             # If f_name is an output column, is it in ctx_df?
                                             # Usually ctx_df is inputs. 
                                             # Let's check. If not, we compute "Target_Value" from results.
                                             pass

                    # 1. Inputs
                    input_feats = [c for c in ctx_df.columns if c.startswith("Input_") or c in results['config']['input_columns']] 
                    # ctx_df usually has "Input_X" naming? 
                    # If not, let's use the list from config
                    input_names = results['config']['input_columns']
                    # We need to map config names to ctx_df columns if they differ. 
                    # Assuming ctx_df has them as-is or we added "Input_".
                    # Let's just use `input_cols` (from valid scope) or `results['config']`.
                    # From previous code: `input_feats = [c for c in ctx_df.columns if c.startswith("Input_")]`
                    if not input_feats:
                         # Fallback if no prefix
                         input_feats = [c for c in input_names if c in ctx_df.columns]
                    
                    plot_grid(input_feats, "Inputs")
                    
                    # 2. Outputs
                    st.markdown("### Outputs")
                    # We need target values in ctx_df for plotting. 
                    # y_true_all (N, T, n_out).
                    # We can take mean target over window for the distribution?
                    mean_targets = np.mean(y_true, axis=1) # (N, n_out)
                    
                    real_output_cols = results['config']['output_columns']
                    
                    # Add to ctx_df safely using Sample_ID mapping
                    for k, out_name in enumerate(real_output_cols):
                        # Create lookup: Index -> Value
                        # mean_targets is (N, n_out). Sample_ID corresponds to 0..N-1
                        # If ctx_df has sample_ids > len(mean_targets), we handle it.
                        
                        # Use map to avoid length mismatch
                        if k < mean_targets.shape[1]:
                             ctx_df[out_name] = ctx_df['Sample_ID'].apply(lambda idx: mean_targets[int(idx), k] if int(idx) < len(mean_targets) else np.nan)
                    
                    plot_grid(real_output_cols, "Outputs")

            # --- Tab 4: Model Relationships ---
            with tab_relationships:
                st.markdown("**Model Relationships (SHAP)**")
                shap_df = results.get('shap_values', pd.DataFrame())
                
                if not shap_df.empty:
                    # Filter by output first
                    outputs = shap_df['Output_Name'].unique()
                    # We need to capture selection from ANY chart.
                    
                    # Logic: Find Sample Indices (or rows) where sel_feat is in range
                    # SHAP df might not have Sample_ID explicitly if we didn't save it.
                    # Assuming shap_df has unique index or we can correspond it.
                    # Usually `metrics.py` creates shap_df. If it's just long format, we might lose sample linkage 
                    # unless we have a 'Sample_ID' column.
                    # If 'Sample_ID' is missing, we can't link effectively.
                    # Let's check `if 'Sample_ID' in shap_df.columns`.
                    # If not, we might need to rely on 'Feature_Value' matching? (Risky).
                    # Or just Color by Feature Value of the selected feature (if applicable).
                    
                    # Assuming we can't easily link samples if ID is missing.
                    # BUT, usually standard melt preserves index? 
                    # If we cannot link, we can just show the plots.
                    # Let's Try to filter by the feature value IN EACH PLOT (only effective for that feature).
                    # To "highlight across trends", we need to know which points in Plot B correspond to points in Plot A.
                    # If we don't have Sample_ID, we can't do "Brush and Link".
                    
                    # Workaround: Just Apply Range Filter to the Viewing Data? 
                    # "Highlighted" means show them in Red, others in Gray.
                    
                    # Strategy: Add 'Color' column to shap_df.
                    # 1. Identify "Selected Indices" based on `sel_feat` within range.
                    #    - We need to know which rows belong to the same "Instance".
                    #    - If `shap_values` uses `obs_id` or index. 
                    #    - Let's assume we can't perfectly link for now if column missing.
                    #    - However, if we assume the order is consistent...
                    
                    # Let's try to highlight just based on the values in the `sel_feat` plot, 
                    # and for others, maybe we can't link without ID.
                    # I will implement the slider for the selected feature.
                    
                    # Better: Filter the DataFrame for plotting.
                    # Actually, if we want to show "relationships", maybe we just color by the selected feature's value?
                    # That is a common pattern (Color by Feature X).
                    # So: Scatter Plot `Feature Y` vs `SHAP Y`, Color = `Feature X Value`.
                    
                    # But user asked: "when data points are selected on one trend, the other trends are highlighted".
                    # This implies binary selection (In Range vs Out).
                    # I'll enable coloring by the "Selection Status" of the `sel_feat`.
                    
                    inputs = shap_df['Feature'].unique()
                    
                    # Ensure indices for linking
                    if 'Sample_ID' not in shap_df.columns:
                         shap_df = shap_df.reset_index(drop=True)
                         shap_df['Global_Index'] = shap_df.index
                    
                    st.info("Select points on any chart to highlight them across all others (Brushing & Linking).")
                    
                    # Store selected indices in Session State
                    if 'shap_selected_indices' not in st.session_state:
                        st.session_state['shap_selected_indices'] = []

                    # Shared highlight mask
                    selected_global_ids = set(st.session_state['shap_selected_indices'])
                    
                    # Helper to render SHAP plots
                    cols = st.columns(2)
                    
                    # Assign Sample_Index per Feature group
                    shap_df['Sample_Index'] = shap_df.groupby(['Feature', 'Output_Name']).cumcount()
                    
                    # Filter by output first
                    outputs = shap_df['Output_Name'].unique()
                     # We need to capture selection from ANY chart.
                    # Streamlit reruns on selection. We check for returned selection data.
                    
                    # Display Loop
                    current_selection_sample_ids = set()
                    
                    for i, feat in enumerate(inputs):
                        # Filter by the selected feature and the current output
                        # We need to iterate over outputs as well, or combine them.
                        # For now, let's just show all outputs for each feature.
                        # This means the plot will have multiple SHAP values for the same feature_value if there are multiple outputs.
                        # This is usually handled by faceting or selecting one output.
                        # Given the removal of output selection, we'll plot all outputs for each feature.
                        feat_df = shap_df[shap_df['Feature'] == feat].copy()
                        
                        # Color logic
                        if not selected_global_ids:
                             feat_df['Color'] = 'blue'
                        else:
                             feat_df['Color'] = np.where(feat_df['Sample_Index'].isin(selected_global_ids), 'red', 'lightgray')
                        
                        fig = px.scatter(feat_df, x='Feature_Value', y='SHAP_Value', color='Color',
                                         color_discrete_map={'blue': 'blue', 'red': 'red', 'lightgray': 'lightgray'},
                                         title=f"SHAP: {feat}")
                        fig.update_layout(showlegend=False, dragmode='select')
                        
                        # Unique key for each chart
                        # IMPORTANT: Removing manual controls. Just brushing/linking. 
                        sel = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode=['box', 'lasso'], key=f"shap_{feat}")
                        
                        # Check if this chart triggered a selection
                        if sel and sel.get('selection'):
                             points = sel['selection'].get('points', [])
                             for p in points:
                                 idx_in_view = p['point_index'] 
                                 real_sample_idx = feat_df.iloc[idx_in_view]['Sample_Index']
                                 current_selection_sample_ids.add(real_sample_idx)

                    # Update state if new selection happened
                    if current_selection_sample_ids:
                        if current_selection_sample_ids != selected_global_ids:
                             st.session_state['shap_selected_indices'] = list(current_selection_sample_ids)
                             st.rerun()
                    elif st.session_state['shap_selected_indices'] and not current_selection_sample_ids:
                         pass
                         
                    if st.button("Clear Selection"):
                        st.session_state['shap_selected_indices'] = []
                        st.rerun()

                    
            # --- Download Artifacts ---
            st.subheader("Downloads")
            import shutil
            
            out_dir = results['output_dir']
            zip_path = f"{out_dir}.zip"
            shutil.make_archive(out_dir, 'zip', out_dir)
            
            with open(zip_path, "rb") as fp:
                    btn = st.download_button(
                        label="Download Experiment Artifacts (ZIP)",
                        data=fp,
                        file_name=f"{run_name}.zip",
                        mime="application/zip"
                    )
    else:
        st.info("Please upload a CSV file or select sample data to proceed.")

# --- PAGE 3: Controller ---
elif st.session_state['current_page'] == "Optimization":
    st.header("PPL Optimizer")
    
    st.subheader("Setup & Upload")
    
    # Initial State
    if 'controller' not in st.session_state:
        st.session_state['controller'] = None
    
    # 1.1 Model Upload (ZIP)
    model_zip = st.file_uploader("Upload Model Artifacts (ZIP)", type="zip")
    
    # 1.2 Data Upload (CSV)
    data_csv = st.file_uploader("Upload Knowledge Base / Scenarios (CSV)", type="csv")
    
    if model_zip and data_csv:
        if st.button("Load Optimizer Environment"):
            try:
                import zipfile
                import yaml
                import shutil
                
                # Extract ZIP to temp
                # In Streamlit Cloud we might use tempfile, here locally we can use a dedicated tmp folder
                output_parent_dir = "../output"
                resolved_parent = os.path.abspath(output_parent_dir)
                temp_dir = os.path.join(resolved_parent, "temp_controller_model")
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                
                with zipfile.ZipFile(model_zip, 'r') as z:
                    z.extractall(temp_dir)
                    
                # Load Config & Identify Root
                config_path = os.path.join(temp_dir, "config.yaml") 
                root_run_dir = temp_dir
                
                # If not in root, search subfolders
                if not os.path.exists(config_path):
                     subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                     if subdirs:
                         root_run_dir = os.path.join(temp_dir, subdirs[0])
                         config_path = os.path.join(root_run_dir, "config.yaml")

                if os.path.exists(config_path):
                    st.session_state['config_path'] = config_path # Store for updates
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                else:
                    st.error("config.yaml not found in ZIP.")
                    st.stop()
                
                # Load Scenarios (User Upload)
                scenario_df = pd.read_csv(data_csv)
                st.session_state['scenario_pool'] = scenario_df
                
                # Load LIME Context (Knowledge Base)
                # Prefer file in ZIP (Training Artifact)
                lime_path = os.path.join(root_run_dir, "lime_context_data.csv")
                lime_df = None
                
                if os.path.exists(lime_path):
                    lime_df = pd.read_csv(lime_path)
                elif 'Output_Name' in scenario_df.columns:
                    # Fallback: User uploaded the context instructions as data?
                    lime_df = scenario_df
                    st.info("Using uploaded CSV as Knowledge Base.")
                else:
                    st.error("Could not find 'lime_context_data.csv' in ZIP, and uploaded CSV is not a valid Knowledge Base.")
                    st.stop()
                
                # Init Controller
                from src.controller_logic import PPLController
                st.session_state['controller'] = PPLController(lime_df=lime_df, config=config)
                st.success("Optimizer Environment Loaded!")
                
            except Exception as e:
                st.error(f"Error loading environment: {e}")

    st.divider()

    # 2. Configuration
    if st.session_state['controller']:
        controller = st.session_state['controller']
        config = controller.config
        
        st.subheader("Configuration")
        
        # 2.1 MV Selection
        all_inputs = config['input_columns']
        all_outputs = config['output_columns']
        
        mvs_selected = st.multiselect("Select Manipulated Variables (MVs)", all_inputs, default=[all_inputs[0]] if all_inputs else [])
        
        # DVs are the rest
        dvs_list = [c for c in all_inputs if c not in mvs_selected]
        
        # MV Configuration
        st.markdown("**Manipulated Variables (MVs)**")
        mvs_config = {}
        cols_mv = st.columns(2)
        for i, mv in enumerate(mvs_selected):
            with cols_mv[i % 2]:
                st.markdown(f"**{mv}**")
                c1, c2 = st.columns(2)
                mn = c1.number_input(f"Min", value=-10.0, key=f"min_{mv}")
                mx = c2.number_input(f"Max", value=100.0, key=f"max_{mv}")
                mvs_config[mv] = {'min': mn, 'max': mx}
                
        st.divider()
        st.markdown("**Controlled Variables (CVs) & Goals**")
        cvs_config = {}
        for cv in all_outputs:
            st.markdown(f"**{cv}**")
            
            c_goal, c_min, c_max = st.columns([0.4, 0.3, 0.3])
            
            with c_goal:
                goal_type = st.selectbox("Goal", ["Target", "Maximize", "Minimize", "N/A"], key=f"goal_type_{cv}")
                target_val = 0.0
                if goal_type == "Target":
                     target_val = st.number_input("Target Value", value=0.0, key=f"target_{cv}")
            
            # Constraints & Priority
            c_min, c_max, c_prio = st.columns([0.3, 0.3, 0.4])
            mn = c_min.number_input("Min", value=-1000.0, key=f"min_{cv}")
            mx = c_max.number_input("Max", value=1000.0, key=f"max_{cv}")
            priority = c_prio.number_input("Priority", value=1, min_value=1, key=f"prio_{cv}", help="Higher value = Higher importance (Cost multiplier)")
            
            # Map Priority to Weight
            # Important: Weight must be POSITIVE for Squared Error Minimization logic.
            # Maximize -> Minimize Negative Error -> Squared Error is minimized.
            # If weight is negative here, we flip the logic.
            # Backend uses target=99999 or -99999. We want state to be CLOSE to target.
            # Cost += Weight * (Val - Target)^2.
            # We want to minimize Cost.
            # So Weight must be Positive.
            # Logic: If goal=Maximize, target=High. Cost=(Val-High)^2. Minimize Cost -> Val -> High. Correct.
            # So Weight = Priority (Positive).
            
            weight = float(priority)
            base_config = {'min': mn, 'max': mx, 'weight': weight}
            
            if goal_type == "Target":
                base_config.update({'target': target_val, 'type': 'Target'})
            elif goal_type == "Maximize":
                 # Target: Large Positive
                 base_config.update({'target': 99999, 'type': 'Max'})
            elif goal_type == "Minimize":
                 # Target: Large Negative
                 base_config.update({'target': -99999, 'type': 'Min'})
            else: # N/A
                 base_config.update({'type': 'None', 'weight': 0.0}) # Zero weight if N/A
                 
            cvs_config[cv] = base_config

        # We can also have a generic objective formula if needed, but CV goals are often enough.
        # Let's keep the formula box just in case.
        st.divider()
        st.markdown("**Global Objective**")
        c_obj, c_goal, c_prio_obj = st.columns([0.5, 0.25, 0.25])
        obj_form = c_obj.text_input("Additional Formula (optional)", help="e.g. `(CV1*10) - (MV1*5)`")
        obj_goal = c_goal.selectbox("Formula Goal", ['max', 'min'])
        obj_prio = c_prio_obj.number_input("Priority", value=10, min_value=1, key="obj_priority", help="Relative to CV priorities")
        
        if st.button("Update Configuration"):
            # Map UI CV config to Controller Logic structure
            controller.configure(mvs_config, {}, cvs_config, obj_form, obj_goal, objective_weight=float(obj_prio))
            
            # Persist to YAML
            if 'config_path' in st.session_state:
                try:
                    import yaml
                    import io
                    import zipfile
                    
                    # 1. Save Config
                    with open(st.session_state['config_path'], 'w') as f:
                        yaml.dump(controller.config, f)
                    
                    st.success(f"Configuration Updated and Saved to disk.")
                    
                    # 2. Create ZIP
                    model_dir = os.path.dirname(st.session_state['config_path'])
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                         for root, dirs, files in os.walk(model_dir):
                             for file in files:
                                 file_path = os.path.join(root, file)
                                 arcname = os.path.relpath(file_path, model_dir)
                                 zip_file.write(file_path, arcname)
                                 
                    # 3. Download Button
                    st.download_button(
                        label="Download Updated Configuration (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="updated_optimizer_config.zip",
                        mime="application/zip",
                        help="Download the updated model configuration for future use."
                    )
                    
                except Exception as e:
                    st.warning(f"Configuration updated in memory, but failed to save/zip file: {e}")
            else:
                st.success("Configuration Updated (In-Memory Only)")
            
    st.divider()
    
    # 3. Control Loop
    st.subheader("Simulation & Control")
    
    if st.session_state['controller']:
        # Simulation Controls
        col_c1, col_c2 = st.columns([0.5, 0.5])
        
        horizon = 20
        history_steps = 20
        pool = st.session_state['scenario_pool']
        current_mvs = st.session_state['controller'].mvs.keys()
        
        start_idx = 0
        manual_trajectory = None
        
        if not pool.empty:
            # Ensure timestamp logic
            if 'timestamp' not in pool.columns:
                 # Should exist from pipeline/upload logic, but fallback
                 pool['timestamp'] = pd.date_range(start='2024-01-01', periods=len(pool), freq='3min')
            
            # Bounds
            max_idx = len(pool) - horizon - 1
            min_idx = history_steps
            if max_idx < min_idx: max_idx = min_idx
            

            # --- Layout: "Simulation Control Panel" ---
            with st.container(): # Group controls
                # Row 1: Strategy with Inline Label
                # Row 1: Strategy with Left Aligned Label
                st.markdown("**Selection Method:**") 
                strategy = st.radio("Method", ["Random Scenario", "Specific Date/Time", "Most Recent Data"], horizontal=True, label_visibility="collapsed")
                
                # Logic for Strategy Selection
                if strategy == "Most Recent Data":
                    st.session_state['sim_start_idx'] = max_idx
                    st.success(f"Simulation will start at the most recent available data point: {pool.iloc[max_idx]['timestamp']}")
                    
                elif strategy == "Specific Date/Time":
                    # Use current state as default
                    curr_i = st.session_state.get('sim_start_idx', min_idx)
                    curr_row = pool.iloc[curr_i]
                    curr_ts = curr_row['timestamp']
                    
                    st.write("**Select Specific Start Time**")
                    c_dt1, c_dt2 = st.columns([0.3, 0.3])
                    sel_date = c_dt1.date_input("Start Date", value=curr_ts.date(), min_value=pool['timestamp'].min().date(), max_value=pool['timestamp'].max().date())
                    sel_time = c_dt2.time_input("Start Time", value=curr_ts.time())
                    
                    # Logic: Auto-update
                    target_ts = pd.Timestamp.combine(sel_date, sel_time)
                    diffs = np.abs(pool['timestamp'] - target_ts)
                    nearest = diffs.idxmin()
                    if nearest < min_idx: nearest = min_idx
                    if nearest > max_idx: nearest = max_idx
                    
                    if nearest != st.session_state.get('sim_start_idx'):
                         st.session_state['sim_start_idx'] = nearest
                         st.rerun()

                elif strategy == "Random Scenario":
                    with st.expander("Filter Scenarios", expanded=True):
                         # ... existing filter logic ...
                         # 1. Variable Filters - RESTRICTED LIST
                        model_vars = list(config.get('input_columns', [])) + list(config.get('output_columns', []))
                        model_vars = sorted(list(set(model_vars)))
                        
                        selected_filters = st.multiselect("Filter by Variable Value Range", options=model_vars)
                        filter_constraints = {}
                        
                        if selected_filters:
                            f_cols = st.columns(min(len(selected_filters), 3))
                            for i, f_var in enumerate(selected_filters):
                                mn, mx = float(pool[f_var].min()), float(pool[f_var].max())
                                if mn == mx: mn, mx = mn - 1, mx + 1
                                with f_cols[i % 3]:
                                    val_range = st.slider(f"{f_var}", min_value=mn, max_value=mx, value=(mn, mx))
                                    filter_constraints[f_var] = val_range

                        # 2. Date Filter
                        use_date_filter = st.checkbox("Filter by Date Range")
                        date_range = []
                        if use_date_filter:
                             if 'timestamp' in pool.columns:
                                 min_date = pool['timestamp'].min().date()
                                 max_date = pool['timestamp'].max().date()
                                 date_range = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
                                 st.info("Click 'Run Simulation' to pick a scenario matching these filters.")
                     # Logic moved to Run button

                # Row 3: Config (Manual Override & Run)
                st.write("---")
                # Removed old Radio "Control Mode"
                
                # Checkbox inside Expander?
                enable_manual = False
                manual_trajectory = None
                
                start_idx = st.session_state.get('sim_start_idx', min_idx)
                if start_idx < min_idx: start_idx = min_idx
                if start_idx > max_idx: start_idx = max_idx
                
                with st.expander("Manual MV Override", expanded=False):
                    enable_manual = st.checkbox("Enable Manual Override", value=False)
                    st.info("Edit trajectory below. If enabled, these values will be applied. Optimizer plan will still be shown for comparison.")
                    
                    init_row = pool.iloc[start_idx]
                    rows = []
                    for t in range(1, horizon + 1):
                         r = {'Step': t}
                         for mv in current_mvs:
                             val = init_row.get(f"Input_{mv}", init_row.get(mv, 0))
                             r[mv] = float(val)
                         rows.append(r)
                    manual_df = pd.DataFrame(rows)
                    manual_trajectory = st.data_editor(manual_df, num_rows="fixed", hide_index=True, key=f"editor_man_{start_idx}")

                # Row 4: Action
                run_clicked = st.button("▶ Run Simulation", type="primary", use_container_width=True)

            # Logic Setup
            start_idx = st.session_state.get('sim_start_idx', min_idx)
            # Clip safe
            if start_idx < min_idx: start_idx = min_idx
            if start_idx > max_idx: start_idx = max_idx
            
                # Removed old Manual Logic block because it's now handled by the checkbox and expander above.


        # Run Logic: Button Triggered
        if run_clicked:
            st.divider()
            # ... Simulation Logic ...
            # 3.1 Pick Scenario
            pool = st.session_state['scenario_pool']
            if not pool.empty:
                import random
                
                # Parameters
                horizon = 20
                history_steps = 20
                
                # Check if pool is large enough
                if len(pool) < (history_steps + horizon):
                    st.error(f"Scenario Pool is too small (needs {history_steps + horizon} samples).")
                else:
                    # 1. Pick Index safe for history & future
                    # Assuming pool is sorted by time if it's a single run? 
                    # If it's a collection of runs, this slicing might cross run boundaries.
                    # For a "Random Scenario" demo, we assume contiguous block is valid.
                    # 0.5 Random Selection Logic (Just-In-Time)
                    if strategy == "Random Scenario":
                         # Re-run filter logic to pick index
                         valid_mask = pd.Series(True, index=pool.index)
                         valid_mask = (pool.index >= min_idx) & (pool.index <= max_idx)
                         
                         # Variable Filters
                         if 'filter_constraints' in locals():
                             if use_date_filter and len(date_range) == 2:
                                  d_mask = (pool['timestamp'].dt.date >= date_range[0]) & (pool['timestamp'].dt.date <= date_range[1])
                                  valid_mask = valid_mask & d_mask
                             
                             for f_v, (f_min, f_max) in filter_constraints.items():
                                  v_mask = (pool[f_v] >= f_min) & (pool[f_v] <= f_max)
                                  valid_mask = valid_mask & v_mask
                             
                             possible_indices = pool[valid_mask].index.tolist()
                             if possible_indices:
                                  new_idx = random.choice(possible_indices)
                                  st.session_state['sim_start_idx'] = new_idx
                                  start_idx = new_idx # Update local var
                             else:
                                  st.error("No scenarios match your filters. Cannot run.")
                                  st.stop()
                         else:
                             st.error("Filter configuration lost.")
                             st.stop()
                    
                    idx = start_idx
                    
                    
                    # 1. Pick Index safe for history & future
                    # ...
                    # 2. Extract History
                    history_slice = pool.iloc[idx - history_steps : idx + 1].copy()
                    
                    # 3. Setup Simulation from Current State
                    current_slice_row = pool.iloc[idx]
                    
                    # Initial Controller State
                    # Inputs from current row
                    initial_state = {col: current_slice_row.get(f"Input_{col}", 0) for col in config['input_columns']}
                    # Outputs from current row (as starting point for CVs)
                    for cv in config['output_columns']:
                        initial_state[cv] = current_slice_row.get(cv, 0)
                        
                    # Simulation Loop (Parallel)
                    sim_state_actual = initial_state.copy()
                    sim_state_auto = initial_state.copy() # Baseline
                    sim_results = []
                    
                    # Record T=0 (Initial State)
                    row_init = {'Step': 0}
                    for cv in config['output_columns']: 
                        row_init[cv] = sim_state_actual.get(cv, 0)
                        row_init[f"Opt_{cv}"] = sim_state_actual.get(cv, 0) # T=0 Baseline
                    for mv in config['input_columns']: 
                        row_init[f"Input_{mv}"] = sim_state_actual.get(mv, 0)
                        row_init[f"Opt_{mv}"] = sim_state_actual.get(mv, 0) # T=0 Baseline
                    sim_results.append(row_init)
                    
                    with st.spinner("Simulating..."):
                         for t in range(1, horizon + 1): # 1 to 20
                             # 1. Path A: Auto Baseline (Parallel World)
                             # Opt plan for auto state
                             action_auto = controller.search_mcts(sim_state_auto, iterations=50, horizon=5)
                             # Step auto state
                             sim_state_auto = controller.step_dmc(sim_state_auto, action_auto)
                             
                             # 2. Path B: Actual Simulation
                             manual_action = {}
                             if manual_trajectory is not None:
                                 try:
                                     target_row = manual_trajectory[manual_trajectory['Step'] == t].iloc[0]
                                     for mv in current_mvs:
                                          target_val = float(target_row.get(mv, 0))
                                          curr_val = sim_state_actual.get(mv, 0)
                                          manual_action[mv] = target_val - curr_val
                                 except:
                                     pass
                             
                             # Determine Actual Action
                             if enable_manual and manual_action:
                                 action_actual = manual_action
                             else:
                                 # FIX: Identity Force
                                 # If manual is disabled, ACTUAL must match AUTO.
                                 action_actual = action_auto
                             
                             # Step Actual State
                             sim_state_actual = controller.step_dmc(sim_state_actual, action_actual)
                             
                             # Record State
                             row = {'Step': t} # Relative future step
                             
                             # Store CVs
                             for cv in config['output_columns']:
                                 row[cv] = sim_state_actual.get(cv, 0)
                                 # Store Auto Baseline CV
                                 row[f"Opt_{cv}"] = sim_state_auto.get(cv, 0)
                                 
                             # Store MVs
                             for mv in current_mvs:
                                 # Actual
                                 mv_val_applied = sim_state_actual.get(mv, 0) 
                                 row[f"Input_{mv}"] = mv_val_applied 
                                 row[mv] = mv_val_applied 
                                 
                                 # Auto Baseline MV
                                 mv_val_auto = sim_state_auto.get(mv, 0)
                                 row[f"Opt_{mv}"] = mv_val_auto
                                 
                             sim_results.append(row)
                    # MVs vs DVs
                    all_inputs = config['input_columns']
                    current_mvs = st.session_state['controller'].mvs.keys()
                    dvs = [c for c in all_inputs if c not in current_mvs]
                    
                    
                    # History Rows
                    # Let's use Step = -20 to 0
                    hist_values = history_slice.reset_index(drop=True)
                    # Len is 21. Indices 0..20.
                    # We want Index 20 -> Step 0. Index 0 -> Step -20.
                    
                    viz_data = [] # Initialize list
                    
                    for i, row in hist_values.iterrows():
                        step_val = i - history_steps 
                        
                        # Pack MVs/DVs
                        for inp in all_inputs:
                            # Try with and without Input_ prefix
                            val = row.get(f"Input_{inp}", row.get(inp, 0))
                            viz_data.append({'Step': step_val, 'Type': 'History', 'Variable': inp, 'Value': val, 'Category': 'MV' if inp in current_mvs else 'DV'})
                            
                        # Pack CVs
                        for cv in config['output_columns']:
                             val = row.get(cv, 0)
                             viz_data.append({'Step': step_val, 'Type': 'History', 'Variable': cv, 'Value': val, 'Category': 'CV'})

                    sim_results_df = pd.DataFrame(sim_results) # Helper
                    
                    # Projected Rows (from Simulation t=0..20)
                    for i, row in enumerate(sim_results):
                        step_val = row['Step']
                        
                        for inp in all_inputs:
                            # Sim results stored as Input_{inp} (from sim loop above)
                             val = row.get(f"Input_{inp}", 0)
                             viz_data.append({'Step': step_val, 'Type': 'Projected', 'Variable': inp, 'Value': val, 'Category': 'MV' if inp in current_mvs else 'DV'})
                             
                             # NEW: Optimizer Baseline (for MVs only)
                             if inp in current_mvs:
                                 # Check if Opt_ value exists
                                 opt_key = f"Opt_{inp}"
                                 if opt_key in row:
                                     opt_val = row[opt_key]
                                     viz_data.append({'Step': step_val, 'Type': 'Optimizer Plan', 'Variable': inp, 'Value': opt_val, 'Category': 'MV'})
                        
                        for cv in config['output_columns']:
                             val = row.get(cv, 0)
                             viz_data.append({'Step': step_val, 'Type': 'Projected', 'Variable': cv, 'Value': val, 'Category': 'CV'})
                             
                             # NEW: Optimizer Baseline for CV
                             # Opt plan for CV
                             opt_key = f"Opt_{cv}"
                             if opt_key in row:
                                 opt_val = row[opt_key]
                                 viz_data.append({'Step': step_val, 'Type': 'Optimizer Plan', 'Variable': cv, 'Value': opt_val, 'Category': 'CV'})

                    viz_df = pd.DataFrame(viz_data)
                    
                    # 5. Rendering
                    
                    # Helper to render a category
                    def render_category(category_name, header_text):
                        with st.expander(header_text, expanded=True):
                            subset = viz_df[viz_df['Category'] == category_name]
                            if subset.empty:
                                st.info("No variables in this category.")
                                return
                                
                            vars_in_cat = subset['Variable'].unique()
                            # Grid Layout
                            cols = st.columns(min(len(vars_in_cat), 4)) 
                            
                            for i, var_name in enumerate(vars_in_cat):
                                with cols[i % len(cols)]:
                                    var_data = subset[subset['Variable'] == var_name]
                                    
                                    # Color Map Logic
                                    # Color Map Logic
                                    if category_name == 'DV':
                                        c_map = {'History': 'gray', 'Projected': 'gray', 'Optimizer Plan': 'blue'} # Opt plan shouldn't exist for DV, but safe fallback
                                        d_map = {'History': 'solid', 'Projected': 'solid', 'Optimizer Plan': 'dot'}
                                    else:
                                        # MV: History(Gray), Projected(Red - Applied), Optimizer(Blue/Green - Comparison)
                                        c_map = {'History': 'gray', 'Projected': 'red', 'Optimizer Plan': '#1f77b4'} # Standard blue
                                        d_map = {'History': 'solid', 'Projected': 'solid', 'Optimizer Plan': 'dot'} # Dotted for Optimizer
                                    
                                    # Ensure consistency 
                                    fig = px.line(var_data, x='Step', y='Value', color='Type', 
                                                  color_discrete_map=c_map,
                                                  line_dash='Type',
                                                  line_dash_map=d_map, # Map types to dash styles
                                                  title=var_name)
                                    # Feedback 4: Hide per-chart legend, use Global Legend
                                    fig.update_layout(showlegend=False, height=200, margin=dict(l=20, r=20, t=30, b=20))
                                    st.plotly_chart(fig, use_container_width=True)
                                
                    
                    
                    # 5.1 Global Legend
                    st.markdown("""
                    <style>
                    .legend-container {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        justify_content: flex-start;
                        gap: 20px;
                        margin-bottom: 15px;
                        margin-left: 5px;
                        font-family: 'Source Sans Pro', sans-serif;
                        font-size: 14px;
                    }
                    .legend-item {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }
                    .line-indicator {
                        width: 20px;
                        height: 0px; /* Line only */
                        border-top: 2px solid;
                    }
                    .solid { border-style: solid; }
                    .dotted { border-style: dotted; } /* Dotted border */
                    
                    /* Custom Colors matching Plotly map */
                    .color-history { border-color: gray; }
                    .color-projected { border-color: red; }
                    .color-opt { border-color: #1f77b4; border-top-width: 3px; border-style: dotted; } /* Blue Dotted */
                    </style>
                    
                    <div class="legend-container">
                        <div class="legend-item">
                            <div class="line-indicator solid color-history"></div>
                            <span>History</span>
                        </div>
                        <div class="legend-item">
                            <div class="line-indicator solid color-projected"></div>
                            <span>Projected (Applied)</span>
                        </div>
                        <div class="legend-item">
                            <div class="line-indicator color-opt"></div> <!-- Dotted check above -->
                            <span>Optimizer Plan</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Render Sections
                    render_category('MV', "Manipulated Variables")
                    render_category('DV', "Disturbance Variables")
                    render_category('CV', "Controlled Variables")
                    
            else:
                st.error("Scenario Pool is empty.")

