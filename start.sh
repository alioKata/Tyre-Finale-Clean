#!/usr/bin/env bash
set -euo pipefail

# echo "Binding port_opener.py to PORT=${PORT:-10000}"
# cat > port_opener.py << 'EOF'
# import socket, os, sys, signal

# PORT = int(os.environ.get('PORT', 10000))
# print(f"Starting port opener on port {PORT}")

# def shutdown(sig, frame):
#     print("Shutting down…")
#     sys.exit(0)
# signal.signal(signal.SIGTERM, shutdown)
# signal.signal(signal.SIGINT, shutdown)

# with socket.socket() as srv:
#     srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     srv.bind(('0.0.0.0', PORT))
#     srv.listen(5)
#     print("Server listening…")
#     while True:
#         conn, _ = srv.accept()
#         conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
#         conn.close()
# EOF

# chmod +x port_opener.py
# exec python port_opener.py

# If Render is invoking us, RENDER will be set
if [[ -n "${RENDER:-}" ]]; then
  HOST="0.0.0.0"
  PORT="${PORT:-10000}"
  echo "🚀 Render detects RENDER env; starting FastAPI on ${HOST}:${PORT}"
  exec uvicorn app.main:app \
       --host "$HOST" \
       --port "$PORT" \
       --lifespan on \
       --workers 1
else
  echo "☁️  start.sh is a production entrypoint; to run locally use:"
  echo "    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
  exit 0
fi