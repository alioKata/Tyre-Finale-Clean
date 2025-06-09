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

# Create a socket listener immediately to help Render detect the port
# Use netcat if available, otherwise use Python
echo "Creating initial port listener on $PORT to help Render detect port..."
if command -v nc > /dev/null; then
  # Start nc in background to listen on the port temporarily
  nc -l -p $PORT &
  NC_PID=$!
  echo "Started netcat listener with PID: $NC_PID"
  sleep 2
  # Kill the netcat process after Render has had time to detect it
  kill $NC_PID || true
elif command -v python3 > /dev/null; then
  # Use Python as an alternative
  python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', $PORT)); s.listen(1); print('Python socket listening temporarily on port $PORT'); import time; time.sleep(2); s.close()" &
  echo "Started Python socket listener"
  sleep 3
fi

# Tell Render we're about to start a service on this port
echo "RENDER_SERVICE_PORT=$PORT" > /tmp/render_port
echo "Ready to start app on port $PORT..."

# Start the application with direct port binding - Explicitly listen on all interfaces
echo "Starting application at $(date) on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75 --log-level debug 