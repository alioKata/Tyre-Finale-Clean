#!/bin/bash
# Set PORT environment variable if not already set
export PORT=${PORT:-8000}
echo "Starting app on port: $PORT"

# Create necessary directories if they don't exist
mkdir -p data/users
mkdir -p app/static/uploads

# List models directory to confirm files are present
echo "Models directory contents:"
ls -la models/

# Start the application with a timeout to avoid hanging
echo "Starting application at $(date)"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75 