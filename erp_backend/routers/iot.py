"""
IoT Telemetry API Router.
Endpoints to retrieve IoT logs, mismatch statistics, and submit telemetry directly.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from erp_backend.database import get_db
from erp_backend.schemas.alert import IoTDiscrepancyRead
from erp_backend.services.telemetry_service import fetch_sensor_telemetry_logs
from iot.telemetry_processor import process_iot_telemetry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/iot", tags=["IoT Sensor Telemetry"])

@router.get("/logs", response_model=List[IoTDiscrepancyRead])
def get_sensor_telemetry_logs(
    sku_id: Optional[str] = Query(None, description="Filter by SKU ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns history log of warehouse weight sensor measurements, showing ERP vs IoT discrepancy rates.
    """
    logs = fetch_sensor_telemetry_logs(db, sku_id, limit, offset)
    return logs

@router.post("/telemetry")
def submit_sensor_telemetry(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Direct HTTP submission of IoT weight telemetry.
    Useful for hackathon demo runs or fallback testing without setting up Mosquitto broker.
    
    Expected format:
    {
        "sensor_id": "SHELF-B04",
        "sku_id": "SKU-9902",
        "weight_grams": 4500,
        "unit_weight_grams": 150,
        "location": "Aisle 3, Shelf B"
    }
    """
    try:
        res = process_iot_telemetry(db, payload)
        return {"status": "success", "data": res}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to process manual telemetry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Telemetry processing database transaction failed")
