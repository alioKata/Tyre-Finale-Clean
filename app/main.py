from pathlib import Path
import os
import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.db import engine, Base, migrate_add_fuel_data
from app.api import auth, pages, tire

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
    # Create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Run migration to add fuel_data column if needed
    try:
        await migrate_add_fuel_data()
        print("Database migration completed successfully")
    except Exception as e:
        print(f"Error during database migration: {e}")

    # # 3) Ensure 'models' directory exists and write class_indices.json
    # os.makedirs(CLASS_INDICES_PATH.parent, exist_ok=True)
    # with open(CLASS_INDICES_PATH, 'w') as f:
    #     json.dump(CLASS_INDICES, f, indent=2)
    # print(f"Wrote class indices to {CLASS_INDICES_PATH}")