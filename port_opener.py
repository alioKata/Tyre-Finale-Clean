import socket, os, sys, signal

PORT = int(os.environ.get('PORT', 10000))
print(f"Starting port opener on port {PORT}")

def shutdown(sig, frame):
    print("Shutting down…")
    sys.exit(0)
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

with socket.socket() as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', PORT))
    srv.listen(5)
    print("Server listening…")
    while True:
        conn, _ = srv.accept()
        conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        conn.close()
