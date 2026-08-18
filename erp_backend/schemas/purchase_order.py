"""Pydantic schemas for Purchase Orders."""
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field


class POCreate(BaseModel):
    supplier_id: str
    sku_id: str
    order_qty: float = Field(..., gt=0)
    unit_cost: Optional[float] = None
    expected_delivery: Optional[date] = None
    notes: Optional[str] = None
    created_by: Optional[str] = "system"


class PORead(BaseModel):
    po_id: int
    po_number: str
    supplier_id: str
    sku_id: str
    order_qty: float
    unit_cost: Optional[float]
    order_date: date
    expected_delivery: Optional[date]
    actual_delivery: Optional[date]
    status: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PORecommendation(BaseModel):
    recommendation_id: str
    sku_id: str
    sku_name: str
    supplier_id: str
    supplier_name: str
    recommended_qty: int
    current_stock: float
    available_stock: float
    incoming_stock: float
    rop: float
    safety_stock: float
    lead_time_demand: float
    target_inventory: float
    supplier_moq: int
    stockout_probability: float
    projected_stockout_date: Optional[str]
    urgency: str                # LOW | MEDIUM | HIGH | CRITICAL
    reason: str
    estimated_cost: Optional[float]


class GRNCreate(BaseModel):
    po_id: int
    received_qty: float = Field(..., gt=0)
    notes: Optional[str] = None
