# app/db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

# Set up logging for SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Use SQLite for database
sqlite_url = "sqlite+aiosqlite:///./app.db"

# engine & session
engine = create_async_engine(sqlite_url, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

# Import models for SQLAlchemy to recognize them
# import app.models.user
# import app.models.verification
import app.models.tire

async def migrate_add_fuel_data():
    """Add fuel_data column to tire_records table if it doesn't exist"""
    from sqlalchemy import text
    
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                # Check if column exists
                check_sql = """
                SELECT COUNT(*) 
                FROM pragma_table_info('tire_records') 
                WHERE name = 'fuel_data'
                """
                result = await session.execute(text(check_sql))
                column_exists = result.scalar()
                
                if not column_exists:
                    print("Adding fuel_data column to tire_records table")
                    # Add the column
                    alter_sql = """
                    ALTER TABLE tire_records 
                    ADD COLUMN fuel_data JSON NULL
                    """
                    await session.execute(text(alter_sql))
                    await session.commit()
                    print("Successfully added fuel_data column")
                else:
                    print("fuel_data column already exists")
        except Exception as e:
            print(f"Error in migration: {e}")
            raise
