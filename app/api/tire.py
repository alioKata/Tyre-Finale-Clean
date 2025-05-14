# app/api/tire.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db import AsyncSessionLocal
from app.services.tire_service import save_and_analyze
from app.models.tire import TireRecordOut, TireRecord
from app.services.user_service import add_upload_record, get_user

router = APIRouter(prefix="/api/tire", tags=["tire"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post(
    "/upload",
    response_model=TireRecordOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_tire_image(
    file: UploadFile = File(...),
    userEmail: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Save incoming file, analyze it, persist and return the new record.
    """
    result = await save_and_analyze(file, db)
    
    # If user email is provided, store the upload record
    if userEmail:
        # Check if user exists
        user = get_user(userEmail)
        if user:
            # Add upload record to user profile
            upload_data = {
                "filename": result.filename,
                "rul_percent": result.rul_percent,
                "id": result.id
            }
            add_upload_record(userEmail, upload_data)
    
    return result

@router.get(
    "/latest",
    response_model=TireRecordOut,
)
async def get_latest_record(db: AsyncSession = Depends(get_db)):
    """
    Return the single most recent TireRecord, or 404 if none exists.
    """
    q = await db.execute(
        select(TireRecord).order_by(TireRecord.upload_time.desc()).limit(1)
    )
    rec = q.scalar_one_or_none()
    if not rec:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No tire records found")
    return rec
