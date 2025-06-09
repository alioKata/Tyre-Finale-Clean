#!/bin/bash

# Make sure script is executable
chmod +x start.sh

# Debug information
echo "Current directory: $(pwd)"
echo "Environment variables:"
env | grep -E 'PORT|RENDER'

# Set PORT environment variable if not already set
# Render sets PORT automatically, so use that value if available
export PORT=${PORT:-8000}
echo "Starting app on port: $PORT"

# Create necessary directories if they don't exist
mkdir -p data/users
mkdir -p app/static/uploads

# List models directory to confirm files are present
echo "Models directory contents:"
ls -la models/

# Start the application with explicit port binding
echo "Starting application at $(date)"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT 