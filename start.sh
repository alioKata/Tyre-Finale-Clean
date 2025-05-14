#!/bin/bash 
python -c "from app.db import migrate_add_fuel_data; import asyncio; asyncio.run(migrate_add_fuel_data())" 
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 
