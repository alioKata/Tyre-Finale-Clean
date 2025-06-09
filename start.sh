#!/bin/bash

# Make sure script is executable
chmod +x start.sh

# Debug information
echo "Current directory: $(pwd)"
echo "Environment variables:"
env | grep -E 'PORT|RENDER'

# Set PORT environment variable - IMPORTANT for Render
# Default to 10000 which is what Render seems to be using based on logs
export PORT=${PORT:-10000}
echo "Starting app on port: $PORT"

# Create necessary directories if they don't exist
mkdir -p data/users
mkdir -p app/static/uploads

# List models directory to confirm files are present
echo "Models directory contents:"
ls -la models/

# Set firewall rules to ensure port is accessible (may help with port detection)
if command -v iptables > /dev/null; then
  echo "Setting firewall rules to allow port $PORT"
  sudo iptables -A INPUT -p tcp --dport $PORT -j ACCEPT || true
fi

# Tell Render we're about to start a service on this port
echo "RENDER_SERVICE_PORT=$PORT" > /tmp/render_port
echo "Ready to start app on port $PORT..."

# Start the application with direct port binding - Explicitly listen on all interfaces
echo "Starting application at $(date) on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75 --log-level debug 