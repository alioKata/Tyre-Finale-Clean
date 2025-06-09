"""
Simple FastAPI application that just binds to the port and responds to health checks.
This can be used to test port binding on Render.
"""

import os
import logging
from fastapi import FastAPI
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_200_OK

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.simple")

# Get port from environment
PORT = int(os.environ.get("PORT", 10000))
logger.info(f"Starting simple app on port {PORT}")

# Initialize FastAPI app
app = FastAPI(title="Simple Port Binder")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return {"message": "Simple port binder is running"}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for health checks"""
    logger.info("Ping endpoint called")
    return Response(content="pong", media_type="text/plain", status_code=HTTP_200_OK)

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint for Render"""
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "healthy", "port": PORT}, status_code=HTTP_200_OK)

@app.get("/ready")
async def ready():
    """Readiness check endpoint"""
    logger.info("Ready endpoint called")
    return JSONResponse(content={"status": "ready", "port": PORT}, status_code=HTTP_200_OK) 