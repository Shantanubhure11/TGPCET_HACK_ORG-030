"""
MQTT Ingestion Service.
Subscribes to warehouse sensor topics, parses weight telemetry,
and triggers the telemetry processor with a database session context.
"""
import json
import logging
import time
import paho.mqtt.client as mqtt

from erp_backend.config import get_settings
from erp_backend.database import get_db_context
from iot.telemetry_processor import process_iot_telemetry

logger = logging.getLogger(__name__)
settings = get_settings()

def on_connect(client, userdata, flags, rc):
    """Callback for MQTT broker connections."""
    if rc == 0:
        logger.info("Connected to MQTT Broker successfully!")
        # Subscribe to all sensor feeds in warehouses
        topic = f"{settings.mqtt_topic_prefix}/#"
        client.subscribe(topic)
        logger.info(f"Subscribed to topic filter: {topic}")
    else:
        logger.error(f"MQTT connection failed with return code {rc}")

def on_message(client, userdata, msg):
    """Callback for incoming MQTT messages."""
    logger.debug(f"Received message on topic: {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        logger.error(f"Failed to decode JSON payload: {e}")
        return

    # Trigger database processing context
    try:
        with get_db_context() as db:
            result = process_iot_telemetry(db, payload)
            logger.info(f"Processed telemetry from {result['sensor_id']} -> discrepancy {result['discrepancy_pct']}%")
    except Exception as e:
        logger.error(f"Database error during telemetry processing: {e}", exc_info=True)

def start_mqtt_listener():
    """Starts the block listener process."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

    broker_host = settings.mqtt_broker
    broker_port = settings.mqtt_port

    logger.info(f"Connecting to MQTT broker at {broker_host}:{broker_port}...")
    try:
        client.connect(broker_host, broker_port, 60)
    except Exception as e:
        logger.error(f"Could not connect to MQTT broker: {e}. Ingestion will not work.")
        return

    # Start loop in background
    client.loop_start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down MQTT Listener...")
        client.loop_stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    start_mqtt_listener()
