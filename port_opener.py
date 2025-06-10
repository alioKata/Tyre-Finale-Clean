import socket, time, os, sys, signal

PORT = int(os.environ.get('PORT', 10000))
print(f"Starting port opener on port {PORT}")

# Clean shutdown on SIGTERM / SIGINT
def shutdown(signum, frame):
    print("Shutdown signal received, exiting.")
    sys.exit(0)
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# Bind & serve forever
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print(f"Server listening on port {PORT}")
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        conn.close()
