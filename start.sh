#!/bin/bash
# Set PORT environment variable if not already set
export PORT=${PORT:-8000}
echo "Starting app on port: $PORT"

# Create necessary directories if they don't exist
mkdir -p data/users
mkdir -p app/static/uploads

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT 