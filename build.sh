#!/bin/bash
# Install Python requirements
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Create the class_indices.json file directly
echo '{
  "good": 0,
  "defective": 1
}' > models/class_indices.json
echo "Created class_indices.json file"

# Download the model file from the correct Google Drive link
pip install gdown
echo "Downloading hybrid_model.h5 from Google Drive..."
gdown 178L9TCIh9IN_Pgw31-0Q4fWaHsgPZTTS -O models/hybrid_model.h5
echo "Download completed. File size: $(du -h models/hybrid_model.h5 | cut -f1)"

# Set permissions for the start script
chmod +x start.sh

# Create data directory for file-based user storage
mkdir -p data/users
mkdir -p app/static/uploads

# Print information for debugging
echo "Model directory contents:"
ls -la models/
echo "Setup complete - PORT is set to: $PORT" 