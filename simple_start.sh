#!/bin/bash

# This is a simplified startup script for diagnosing port binding issues on Render

# Display debug information
echo "Current directory: $(pwd)"
echo "Environment variables:"
env | grep -E 'PORT|RENDER'

# Set PORT environment variable (default to 10000)
export PORT=${PORT:-10000}
echo "Starting simple app on port: $PORT"

# Create indicator files for Render
echo "PORT=$PORT" > /tmp/render_port
echo "PORT=$PORT" > /tmp/render_port_file
echo "port=$PORT" > .render-port-info

# Direct port binding with nc (netcat) if available
if command -v nc > /dev/null; then
    echo "Starting netcat on port $PORT to ensure early port binding"
    (
        # Start nc in background and keep it running for 60 seconds
        nc -l -p $PORT &
        NC_PID=$!
        echo "Netcat started with PID: $NC_PID"
        sleep 60
        kill $NC_PID || true
    ) &
fi

# Start the simple app
echo "Starting simple FastAPI application on port $PORT"
exec uvicorn app.simple_main:app --host 0.0.0.0 --port $PORT --log-level debug 