"""Pydantic schemas for Supplier."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    country: Optional[str] = None
    avg_lead_time: float = Field(3.0, ge=0, description="Average lead time in days")
    lead_time_std: float = Field(0.5, ge=0, description="Std dev of lead time")
    reliability_pct: float = Field(95.0, ge=0, le=100)
    moq: int = Field(1, ge=1)
    capacity: int = Field(10000, ge=1)


class SupplierCreate(SupplierBase):
    supplier_id: str = Field(..., min_length=1, max_length=20)


class SupplierRead(SupplierBase):
    supplier_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierPerformance(BaseModel):
    supplier_id: str
    name: str
    on_time_delivery_pct: float
    avg_lead_time_days: float
    lead_time_std: float
    total_orders: int
    pending_orders: int
    moq: int
