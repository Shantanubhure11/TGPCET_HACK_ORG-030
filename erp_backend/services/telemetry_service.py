"""
Telemetry Service.
Provides access to IoT sensor reading logs and discrepancy records.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from erp_backend.models.sensor_log import SensorLog
from erp_backend.models.item import Item

logger = logging.getLogger(__name__)

def fetch_sensor_telemetry_logs(
    db: Session,
    sku_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> list:
    """
    Fetches raw sensor log history, including discrepancy details.
    """
    query = db.query(SensorLog)
    if sku_id:
        query = query.filter(SensorLog.sku_id == sku_id)
        
    query = query.order_by(desc(SensorLog.timestamp))
    rows = query.offset(offset).limit(limit).all()
    
    results = []
    for row in rows:
        item = db.query(Item).filter(Item.sku_id == row.sku_id).first()
        results.append({
            "log_id": row.log_id,
            "sensor_id": row.sensor_id,
            "sku_id": row.sku_id,
            "sku_name": item.name if item else "Unknown",
            "calculated_quantity": float(row.calculated_quantity) if row.calculated_quantity else 0.0,
            "erp_quantity_at_time": float(row.erp_quantity_at_time) if row.erp_quantity_at_time else 0.0,
            "discrepancy_qty": float(row.discrepancy_qty) if row.discrepancy_qty else 0.0,
            "discrepancy_pct": float(row.discrepancy_pct) if row.discrepancy_pct else 0.0,
            "alert_flag": row.alert_flag,
            "alert_level": row.alert_level,
            "timestamp": row.timestamp.isoformat(),
            "location": row.location
        })
    return results

from typing import Optional
