# app/models/tire.py

from sqlalchemy import Column, Integer, String, DateTime, Float, func, JSON
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

from app.db import Base

class TireRecord(Base):
    __tablename__ = "tire_records"

    id           = Column(Integer, primary_key=True, index=True)
    filename     = Column(String, nullable=False)
    upload_time  = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False)
    rul_percent  = Column(Float, nullable=False)
    fuel_data    = Column(JSON, nullable=True)  # Store fuel consumption estimates
    
    def __repr__(self):
        """String representation of the TireRecord model"""
        return f"<TireRecord(id={self.id}, file={self.filename}, rul={self.rul_percent}%, time={self.upload_time})>"

class FuelConsumptionData(BaseModel):
    rul_percentage: float
    estimated_annual_consumption: float
    consumption_new_tire: int
    consumption_worn_tire: int
    annual_extra_cost_vs_new: float
    annual_potential_savings_vs_worn: float
    disclaimer: str

class TireRecordOut(BaseModel):
    id: int
    filename: str
    upload_time: datetime
    rul_percent: float
    fuel_data: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}
    
    def dict(self, *args, **kwargs):
        """Custom dict method to ensure fuel_data is properly serialized"""
        d = super().dict(*args, **kwargs)
        # Ensure fuel_data is a proper dict if it exists
        if d.get("fuel_data") is not None and not isinstance(d["fuel_data"], dict):
            d["fuel_data"] = dict(d["fuel_data"])
        return d
