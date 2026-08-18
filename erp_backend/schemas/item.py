"""Pydantic schemas for Item (SKU)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    unit: str = "units"
    unit_cost: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    supplier_id: Optional[str] = None
    moq: int = Field(1, ge=1)


class ItemCreate(ItemBase):
    sku_id: str = Field(..., min_length=1, max_length=20)


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    supplier_id: Optional[str] = None
    moq: Optional[int] = None


class ItemRead(ItemBase):
    sku_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
