"""
IoT MQTT telemetry ingestion package.
Subscribes to sensor readings, checks discrepancies vs ERP, and logs alerts.
"""
from iot.telemetry_processor import process_iot_telemetry

__all__ = ["process_iot_telemetry"]
