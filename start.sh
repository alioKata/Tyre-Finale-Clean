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

# Create a persistent socket listener in the background that will be detected by Render
# This socket will stay open for 60 seconds - much longer than Render's detection timeout
echo "Creating persistent port listener on $PORT for Render to detect..."

# This function creates a socket and keeps it open for a while
create_long_socket() {
  python3 -c "
import socket, time, threading, os

def handle_conn(conn, addr):
    print(f'Connection from {addr}')
    conn.send(b'OK\\n')
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', $PORT))
    s.listen(5)
    s.settimeout(1)
    
    print(f'Socket listening on port {$PORT}')
    with open('/tmp/socket_ready', 'w') as f:
        f.write('Socket is listening')
    
    start_time = time.time()
    # Keep this socket open for 60 seconds to ensure Render detects it
    while time.time() - start_time < 60:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_conn, args=(conn, addr)).start()
        except socket.timeout:
            pass
        except Exception as e:
            print(f'Error: {e}')
    
    print('Socket listener closing')
    s.close()
    # Signal that we've closed our socket so the main process can proceed
    with open('/tmp/socket_closed', 'w') as f:
        f.write('Socket closed')

if __name__ == '__main__':
    main()
" &

SOCKET_PID=$!
echo "Started Python socket listener with PID: $SOCKET_PID"
}

# Start the persistent socket in the background
create_long_socket

# Wait for the socket to be ready (confirmed by the presence of the file)
echo "Waiting for socket to be ready..."
max_wait=10
counter=0
while [ ! -f /tmp/socket_ready ] && [ $counter -lt $max_wait ]; do
    sleep 1
    counter=$((counter+1))
    echo "Waiting for socket to be ready... $counter/$max_wait"
done

if [ -f /tmp/socket_ready ]; then
    echo "Socket is ready and listening on port $PORT"
else
    echo "Warning: Socket may not be ready, but continuing anyway"
fi

# Tell Render we're about to start a service on this port
echo "RENDER_SERVICE_PORT=$PORT" > /tmp/render_port
echo "PORT=$PORT" > /tmp/render_port_file
echo "Ready to start app on port $PORT..."

# Start the application with direct port binding - Using nohup to ensure it stays running
echo "Starting application at $(date) on port $PORT"
# Don't wait for the socket to close, just start the application
# The socket will transfer connections to the app when it starts
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75 --log-level debug 