"""
IoT Telemetry Processor.
Validates raw MQTT sensor readings, calculates weight-to-qty conversions,
computes ERP vs IoT inventory discrepancies, and records results/alerts in database.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session
from erp_backend.models.inventory import Inventory
from erp_backend.models.sensor_log import SensorLog
from erp_backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def process_iot_telemetry(db: Session, payload: dict) -> dict:
    """
    Process incoming MQTT telemetry payload.
    
    Expected payload:
    {
        "sensor_id": str,
        "sku_id": str,
        "weight_grams": float,
        "unit_weight_grams": float,
        "timestamp": str (ISO 8601),
        "location": Optional[str]
    }
    """
    sensor_id = payload.get("sensor_id")
    sku_id = payload.get("sku_id")
    weight_grams = float(payload.get("weight_grams", 0))
    unit_weight_grams = float(payload.get("unit_weight_grams", 1.0))
    location = payload.get("location", "unknown")

    if not sensor_id or not sku_id:
        raise ValueError("Invalid payload: sensor_id and sku_id are required fields")

    # 1. Convert weight to count quantity
    detected_qty = float(round(weight_grams / unit_weight_grams, 2))

    # 2. Fetch current ERP inventory balance (across all warehouses for this SKU)
    # For demo simplicity, sum all warehouses or find the inventory record in location
    inv_record = db.query(Inventory).filter(Inventory.sku_id == sku_id).first()
    erp_qty = float(inv_record.physical_stock) if inv_record else 0.0

    # 3. Calculate discrepancies
    discrepancy_qty = float(round(abs(detected_qty - erp_qty), 2))
    discrepancy_pct = float(round((discrepancy_qty / erp_qty * 100.0), 2)) if erp_qty > 0 else 0.0
    if erp_qty == 0.0 and detected_qty > 0.0:
        discrepancy_pct = 100.0 # Full mismatch

    # 4. Determine alert flags based on config thresholds
    alert_flag = False
    alert_level = "INFO"
    
    if discrepancy_pct > settings.alert_threshold_pct:
        alert_flag = True
        if discrepancy_pct >= 25.0: # CRITICAL limit
            alert_level = "CRITICAL"
        else:
            alert_level = "WARNING"

    # 5. Insert SensorLog entry
    log_entry = SensorLog(
        sensor_id=sensor_id,
        sku_id=sku_id,
        measured_weight_grams=weight_grams,
        unit_weight_grams=unit_weight_grams,
        calculated_quantity=detected_qty,
        erp_quantity_at_time=erp_qty,
        discrepancy_qty=discrepancy_qty,
        discrepancy_pct=discrepancy_pct,
        alert_flag=alert_flag,
        alert_level=alert_level,
        timestamp=datetime.utcnow(),
        location=location
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    # 6. Trigger alert record creation if threshold exceeded
    if alert_flag:
        logger.warning(
            f"IoT Discrepancy Alert! SKU {sku_id} on sensor {sensor_id}: "
            f"IoT Quantity={detected_qty}, ERP Quantity={erp_qty} (Diff={discrepancy_pct}%)"
        )
        # Import alert service locally to prevent circular dependency
        from erp_backend.services.alert_service import create_system_alert
        create_system_alert(
            alert_type="IOT_DISCREPANCY",
            severity=alert_level,
            sku_id=sku_id,
            sensor_id=sensor_id,
            message=(
                f"IoT Inventory Discrepancy: sensor {sensor_id} reports {detected_qty:.0f} units, "
                f"but ERP system records {erp_qty:.0f} units. Mismatch is {discrepancy_pct:.1f}%."
            ),
            details={
                "sensor_id": sensor_id,
                "sku_id": sku_id,
                "detected_qty": detected_qty,
                "erp_qty": erp_qty,
                "discrepancy_pct": discrepancy_pct,
                "location": location
            }
        )

    return {
        "log_id": log_entry.log_id,
        "sensor_id": sensor_id,
        "sku_id": sku_id,
        "calculated_quantity": detected_qty,
        "erp_quantity": erp_qty,
        "discrepancy_qty": discrepancy_qty,
        "discrepancy_pct": discrepancy_pct,
        "alert_flag": alert_flag,
        "alert_level": alert_level,
        "timestamp": log_entry.timestamp.isoformat(),
        "location": location
    }
