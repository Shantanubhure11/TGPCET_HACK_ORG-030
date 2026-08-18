"""
Alerts API Router.
Queries active system alerts (stockouts, overstock, IoT discrepancies) and handles acknowledgements.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from erp_backend.schemas.alert import AlertRead, AlertAcknowledge
from erp_backend.services.alert_service import get_active_alerts, acknowledge_system_alert

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["System Alerts"])

@router.get("/active", response_model=List[AlertRead])
def get_system_alerts(
    alert_type: Optional[str] = Query(None, description="STOCKOUT | OVERSTOCK | IOT_DISCREPANCY"),
    severity: Optional[str] = Query(None, description="INFO | WARNING | CRITICAL")
):
    """
    Returns lists of all current, active (unacknowledged) inventory alerts.
    """
    alerts = get_active_alerts(alert_type, severity)
    return alerts

@router.post("/acknowledge")
def acknowledge_alert(
    payload: AlertAcknowledge
):
    """
    Acknowledge an alert to dismiss it from active warnings.
    """
    res = acknowledge_system_alert(
        alert_id=payload.alert_id,
        user_id=payload.user_id,
        notes=payload.notes
    )
    
    if not res:
        raise HTTPException(status_code=404, detail="Alert ID not found or already acknowledged")
        
    return {"status": "success", "message": "Alert acknowledged successfully", "alert": res}
