"""Pydantic schemas for Inventory."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryRead(BaseModel):
    inventory_id: int
    sku_id: str
    warehouse_id: str
    physical_stock: float
    allocated_stock: float
    available_stock: float
    incoming_stock: float
    safety_stock: float
    rop: float
    days_of_inventory: Optional[float] = None
    stock_status: Optional[str] = None          # GREEN / YELLOW / RED
    stockout_probability: Optional[float] = None
    risk_level: Optional[str] = None
    last_counted_at: Optional[datetime] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class InventoryAdjust(BaseModel):
    sku_id: str
    warehouse_id: str
    qty_change: float = Field(..., description="Positive = add, Negative = subtract")
    reason: str = Field(..., min_length=3)
    user_id: Optional[str] = "system"
    notes: Optional[str] = None


class LedgerEntryRead(BaseModel):
    ledger_id: int
    sku_id: str
    warehouse_id: Optional[str]
    transaction_type: str
    reference_id: Optional[str]
    qty_change: float
    previous_balance: Optional[float]
    new_balance: Optional[float]
    timestamp: datetime
    user_id: Optional[str]
    notes: Optional[str]

    model_config = {"from_attributes": True}
