# #!/bin/bash
# # Install Python requirements
# pip install -r requirements.txt

# # Create models directory
# mkdir -p models

# # Create the class_indices.json file directly
# echo '{
#   "good": 0,
#   "defective": 1
# }' > models/class_indices.json
# echo "Created class_indices.json file"

# # Instead of downloading the model file at build time, add gdown to ensure it's available
# pip install gdown
# echo "Installed gdown for on-demand model downloading"

# # Create port binding indicator files to ensure render knows we'll bind to a port
# PORT=${PORT:-10000}
# echo "Ensuring web service binds to port: $PORT"

# # Create multiple indicator files - Render checks for these
# mkdir -p tmp
# echo "PORT=$PORT" > tmp/port_info.txt
# echo "port=$PORT" > .render-port-info
# echo "PORT=$PORT" > /tmp/render_port
# echo "PORT=$PORT" > /tmp/port

# # Set permissions for the start script
# chmod +x start.sh

# # Create data directory for file-based user storage
# mkdir -p data/users
# mkdir -p app/static/uploads

# # Print information for debugging
# echo "Environment variables:"
# env | grep -E 'PORT|RENDER'
# echo "Setup complete - PORT is set to: $PORT" 





#!/bin/bash
set -euo pipefail

# 1. Install Python requirements
pip install -r requirements.txt

# 2. Create models directory and class indices
mkdir -p models
cat > models/class_indices.json << 'EOF'
{
  "good": 0,
  "defective": 1
}
EOF
echo "Created class_indices.json file"

# 3. Install gdown for on-demand model downloads
pip install gdown
echo "Installed gdown for on-demand model downloading"

# 4. Ensure start.sh is executable
chmod +x start.sh

# 5. Create storage dirs
mkdir -p data/users
mkdir -p app/static/uploads

# 6. Debug info
echo "Environment variables:"
env | grep -E 'PORT|RENDER'
echo "Setup complete"
