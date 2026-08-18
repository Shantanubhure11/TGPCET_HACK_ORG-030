"""Pydantic schemas for Alerts and IoT discrepancies."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertRead(BaseModel):
    alert_id: str
    alert_type: str         # STOCKOUT | OVERSTOCK | IOT_DISCREPANCY | SUPPLIER_DELAY
    severity: str           # INFO | WARNING | CRITICAL
    sku_id: Optional[str] = None
    sensor_id: Optional[str] = None
    message: str
    details: Optional[dict] = None
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime


class IoTDiscrepancyRead(BaseModel):
    log_id: int
    sensor_id: str
    sku_id: Optional[str]
    sku_name: Optional[str] = None
    calculated_quantity: Optional[float]
    erp_quantity_at_time: Optional[float]
    discrepancy_qty: Optional[float]
    discrepancy_pct: Optional[float]
    alert_flag: bool
    alert_level: Optional[str]
    timestamp: datetime
    location: Optional[str]

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    alert_id: str
    user_id: str
    notes: Optional[str] = None
