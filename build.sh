#!/bin/bash
# Install Python requirements
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Instead of downloading from Google Drive, just create the class_indices.json file directly
echo '{
  "good": 0,
  "defective": 1
}' > models/class_indices.json
echo "Created class_indices.json file"

# Download only the model file
pip install gdown
gdown 1ceCHkTJu9_YsE00pFW_zhB91AUuQas4- -O models/hybrid_model.h5

# Set permissions for the start script
chmod +x start.sh

# Create data directory for file-based user storage
mkdir -p data/users
mkdir -p app/static/uploads

# Print information for debugging
echo "Model directory contents:"
ls -la models/
echo "Setup complete - PORT is set to: $PORT" 