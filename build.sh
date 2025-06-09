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

# Download the model file ONLY if it doesn't exist or is too small
if [ ! -f "models/hybrid_model.h5" ] || [ $(du -k "models/hybrid_model.h5" | cut -f1) -lt 1000 ]; then
  echo "Downloading hybrid_model.h5 from Google Drive..."
  pip install gdown
  gdown 178L9TCIh9IN_Pgw31-0Q4fWaHsgPZTTS -O models/hybrid_model.h5
  echo "Download completed. File size: $(du -h models/hybrid_model.h5 | cut -f1)"
else
  echo "Model file already exists, skipping download. Size: $(du -h models/hybrid_model.h5 | cut -f1)"
fi

# Create port binding indicator files to ensure render knows we'll bind to a port
PORT=${PORT:-10000}
echo "Ensuring web service binds to port: $PORT"

# Create multiple indicator files - Render checks for these
mkdir -p tmp
echo "PORT=$PORT" > tmp/port_info.txt
echo "port=$PORT" > .render-port-info
echo "PORT=$PORT" > /tmp/render_port
echo "PORT=$PORT" > /tmp/port

# Set permissions for the start script
chmod +x start.sh

# Create data directory for file-based user storage
mkdir -p data/users
mkdir -p app/static/uploads

# Print information for debugging
echo "Model directory contents:"
ls -la models/
echo "Environment variables:"
env | grep -E 'PORT|RENDER'
echo "Setup complete - PORT is set to: $PORT" 