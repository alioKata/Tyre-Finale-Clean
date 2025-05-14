#!/bin/bash
# Install Python requirements
pip install -r requirements.txt

# Install gdown to download from Google Drive
pip install gdown

# Create models directory
mkdir -p models

# Download model files from Google Drive
gdown 1ceCHkTJu9_YsE00pFW_zhB91AUuQas4- -O models/hybrid_model.h5
gdown 178L9TCIh9IN_Pgw31-0Q4fWaHsgPZTTS -O models/class_indices.json

# Set permissions for the start script
chmod +x start.sh 