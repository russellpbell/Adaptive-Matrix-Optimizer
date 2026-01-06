#!/bin/bash

# Configuration for robust startup on macOS with TensorFlow
export TF_CPP_MIN_LOG_LEVEL=3
export TF_ENABLE_ONEDNN_OPTS=0
export GRPC_POLL_STRATEGY=poll
export KMP_DUPLICATE_LIB_OK=TRUE
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Activate environment and run with File Watcher DISABLED
source .venv/bin/activate
streamlit run ppl-model-pipeline/app.py --server.fileWatcherType=none
