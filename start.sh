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

# Create a simple port binding script
cat > port_opener.py << EOF
import socket
import time
import sys
import os
import signal
import threading

PORT = int(os.environ.get('PORT', 10000))
print(f"Starting port opener on port {PORT}")

def handle_sigterm(signum, frame):
    print(f"Received signal {signum}, exiting...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal.SIG_IGN)

def run_server():
    # Create socket and bind to the port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('0.0.0.0', PORT))
        server.listen(5)
        print(f"Server listening on port {PORT}")
        
        # Write indicator file
        with open("/tmp/port_bound", "w") as f:
            f.write(f"Port {PORT} bound at {time.time()}")
            
        # Keep accepting connections for 2 minutes
        server.settimeout(1)
        start_time = time.time()
        while time.time() - start_time < 120:  # Run for 2 minutes
            try:
                conn, addr = server.accept()
                print(f"Connection from {addr}")
                conn.send(b"HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nOK")
                conn.close()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Failed to bind to port {PORT}: {e}")
        sys.exit(1)
    finally:
        print(f"Closing server on port {PORT}")
        server.close()

# Start in a separate thread
thread = threading.Thread(target=run_server)
thread.daemon = True
thread.start()

# Wait for a while to let Render detect the port
print("Port opener running, waiting for detection...")
time.sleep(3600)  # Keep running for 1 hour
EOF

# Create necessary directories
mkdir -p data/users
mkdir -p app/static/uploads

# Run the port opener in the background 
echo "Starting dedicated port opener script"
python3 port_opener.py &
PORT_OPENER_PID=$!
echo "Port opener started with PID: $PORT_OPENER_PID"

# Wait for the port opener to establish the socket
sleep 5

# Tell Render we're about to start the application
echo "RENDER_SERVICE_PORT=$PORT" > /tmp/render_port
echo "PORT=$PORT" > /tmp/render_port_file
echo "Starting application on port $PORT"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug 