from pathlib import Path
import os
import json
import logging
import sys
import socket
import threading
import time
import signal

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_200_OK

from app.db import engine, Base, migrate_add_fuel_data
from app.api import auth, pages, tire
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Log system information
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Environment PORT: {os.environ.get('PORT')}")
logger.info(f"Settings PORT: {settings.PORT}")

# Global socket variable to keep reference for cleanup
early_socket = None

# Early port binding to help Render detect the service
def create_early_socket_binding():
    global early_socket
    try:
        # Create a socket that will be detected by Render's port scanner
        early_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        early_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        early_socket.bind(('0.0.0.0', settings.PORT))
        early_socket.listen(5)
        logger.info(f"Created early socket binding on port {settings.PORT}")
        
        # Create a simple handler that sends a response to any connection
        def handle_connections():
            while True:
                try:
                    # Accept connection with a 1-second timeout
                    early_socket.settimeout(1)
                    try:
                        conn, addr = early_socket.accept()
                        logger.info(f"Received early connection from {addr}")
                        try:
                            conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\npong")
                        finally:
                            conn.close()
                    except socket.timeout:
                        pass
                except Exception as e:
                    if early_socket is None:  # Socket was closed
                        break
                    logger.error(f"Error in socket connection handler: {e}")
        
        # Start a thread to handle connections
        socket_thread = threading.Thread(target=handle_connections, daemon=True)
        socket_thread.start()
        logger.info("Started early socket connection handler thread")

        file = os.path.dirname(__file__)
        file = file[0:file.find("\\app")]
        # Write a file that Render can check
        with open(f"{file}\\tmp\\port_bound.txt", "w") as f:
            f.write(f"PORT {settings.PORT} bound at {time.time()}\n")
            
        # Register a function to close the socket when uvicorn binds to the port
        def close_socket_when_app_starts():
            # Wait for 60 seconds before closing the early socket
            # This ensures Render has plenty of time to detect the port
            time.sleep(60)
            global early_socket
            if early_socket:
                logger.info(f"Closing early socket binding on port {settings.PORT}")
                s = early_socket
                early_socket = None
                try:
                    s.close()
                except Exception as e:
                    logger.error(f"Error closing early socket: {e}")
        
        # Start a thread to close the socket after delay
        closer_thread = threading.Thread(target=close_socket_when_app_starts, daemon=True)
        closer_thread.start()
        
    except Exception as e:
        logger.error(f"Error creating early socket binding: {e}")

# Create signal handlers for graceful shutdown
def setup_signal_handlers():
    def handle_sigterm(signum, frame):
        logger.info("Received SIGTERM signal, shutting down gracefully")
        # Close early socket if still open
        global early_socket
        if early_socket:
            try:
                logger.info("Closing early socket binding during shutdown")
                early_socket.close()
                early_socket = None
            except Exception as e:
                logger.error(f"Error closing early socket during shutdown: {e}")
        # Exit gracefully
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    logger.info("Registered signal handlers for graceful shutdown")

# Attempt early port binding if not running in debug mode
if not os.environ.get("DEBUG"):
    create_early_socket_binding()
    setup_signal_handlers()

# Base directory of this module
BASE_DIR = Path(__file__).parent

# Class indices mapping and path
CLASS_INDICES = {"good": 0, "defective": 1}
CLASS_INDICES_PATH = BASE_DIR.parent / "models" / "class_indices.json"

# Custom StaticFiles to disable caching in browser
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

# Initialize FastAPI app
app = FastAPI(title="AliProject API")
logger.info(f"Initializing app with host={settings.HOST}, port={settings.PORT}")

# Mount static files with no-cache behavior
app.mount(
    "/static",
    NoCacheStaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

# Include API routers
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(tire.router)

@app.on_event("startup")
async def on_startup():
    try:
        # Create directories
        logger.info("Creating necessary directories")
        os.makedirs(os.path.join("data", "users"), exist_ok=True)
        os.makedirs(os.path.join("app", "static", "uploads"), exist_ok=True)
        
        # Create all database tables
        logger.info("Creating database tables")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Run migration to add fuel_data column if needed
        try:
            logger.info("Running database migration")
            await migrate_add_fuel_data()
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            # Continue even if migration fails

        # Ensure models directory exists
        logger.info("Checking models directory")
        os.makedirs(Path(CLASS_INDICES_PATH).parent, exist_ok=True)
        
        # Write class_indices.json if it doesn't exist
        if not os.path.exists(CLASS_INDICES_PATH):
            logger.info(f"Creating class indices file at {CLASS_INDICES_PATH}")
            with open(CLASS_INDICES_PATH, 'w') as f:
                json.dump(CLASS_INDICES, f, indent=2)
        
        # Write port info to a file that Render can detect
        print(f"Path is {os.path.dirname(__file__)}/tmp/render_port_info.txt")
        file = os.path.dirname(__file__)
        file = file[0:file.find("\\app")]
        print(f"Path is {file}")

        with open(f"{file}\\tmp\\render_port_info.txt", "w") as f:
            f.write(f"PORT={settings.PORT}\n")
            
        logger.info(f"Application startup complete. Running on {settings.HOST}:{settings.PORT}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Raise to ensure the app doesn't silently fail
        raise

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutting down")
    # Close the early socket if it's still open
    global early_socket
    if early_socket:
        try:
            logger.info("Closing early socket binding during shutdown")
            early_socket.close()
            early_socket = None
        except Exception as e:
            logger.error(f"Error closing early socket during shutdown: {e}")
    logger.info("Shutdown complete")

@app.get("/")
async def root():
    """Root endpoint that redirects to welcome page"""
    return {"message": "API is running", "redirect_to": "/welcome.html"}

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint for Render"""
    return {"status": "healthy", "port": settings.PORT}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for health checks"""
    return Response(content="pong", media_type="text/plain", status_code=HTTP_200_OK)

@app.get("/ready")
async def ready():
    """Readiness check endpoint"""
    return JSONResponse(content={"status": "ready", "port": settings.PORT})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request error: {e}")
        raise