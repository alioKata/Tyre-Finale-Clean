from pathlib import Path
import os
import json
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.db import engine, Base, migrate_add_fuel_data
from app.api import auth, pages, tire
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

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
        
        logger.info(f"Application startup complete. Running on {settings.HOST}:{settings.PORT}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Raise to ensure the app doesn't silently fail
        raise

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint for Render"""
    return {"status": "healthy"}