"""
Alert Service.
Manages transient and active inventory alerts in memory (discrepancies, low stock, stockouts).
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

# Global in-memory alerts database for simple hackathon demo setup
SYSTEM_ALERTS = []

def create_system_alert(
    alert_type: str,
    severity: str,
    sku_id: Optional[str] = None,
    sensor_id: Optional[str] = None,
    message: str = "",
    details: Optional[dict] = None
) -> dict:
    """
    Creates a new alert record.
    Types: STOCKOUT | OVERSTOCK | IOT_DISCREPANCY | SUPPLIER_DELAY
    Severity: INFO | WARNING | CRITICAL
    """
    alert = {
        "alert_id": f"alt-{uuid.uuid4().hex[:6]}",
        "alert_type": alert_type,
        "severity": severity,
        "sku_id": sku_id,
        "sensor_id": sensor_id,
        "message": message,
        "details": details or {},
        "is_acknowledged": False,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Prepend to alerts list
    SYSTEM_ALERTS.insert(0, alert)
    
    # Cap alerts list size to 200 items
    if len(SYSTEM_ALERTS) > 200:
        SYSTEM_ALERTS.pop()
        
    logger.info(f"System Alert Registered [{alert_type}] - {severity}: {message}")
    return alert

def get_active_alerts(alert_type: Optional[str] = None, severity: Optional[str] = None) -> List[dict]:
    """
    Query active unacknowledged alerts.
    """
    results = [a for a in SYSTEM_ALERTS if not a["is_acknowledged"]]
    
    if alert_type:
        results = [a for a in results if a["alert_type"] == alert_type]
    if severity:
        results = [a for a in results if a["severity"] == severity]
        
    return results

def acknowledge_system_alert(alert_id: str, user_id: str, notes: Optional[str] = None) -> Optional[dict]:
    """
    Marks an alert as acknowledged.
    """
    for alert in SYSTEM_ALERTS:
        if alert["alert_id"] == alert_id:
            alert["is_acknowledged"] = True
            alert["acknowledged_by"] = user_id
            alert["acknowledged_at"] = datetime.utcnow().isoformat()
            if notes:
                alert["details"]["acknowledgement_notes"] = notes
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return alert
    return None

def clear_all_alerts():
    """Reset system alerts."""
    global SYSTEM_ALERTS
    SYSTEM_ALERTS = []
