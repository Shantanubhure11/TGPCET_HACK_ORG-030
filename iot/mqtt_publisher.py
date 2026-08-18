"""
Simulated MQTT Publisher.
Sends mock inventory weights to Mosquitto MQTT broker for testing and hackathon live demonstrations.
"""
import json
import logging
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

from erp_backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def generate_mock_payload(sensor_id: str, sku_id: str, location: str, match_erp: bool = True) -> dict:
    """
    Generates a realistic weight reading.
    If match_erp is False, we generate a randomized discrepancy (understock or overstock).
    """
    unit_weight = 150.0  # grams per unit
    target_units = random.randint(30, 80)
    
    if not match_erp:
        # Simulate discrepancy (either shelf holds less units or unit weighs differently)
        target_units += random.choice([-20, -10, 15, 25])
        target_units = max(5, target_units)
        
    weight_grams = target_units * unit_weight

    return {
        "sensor_id": sensor_id,
        "sku_id": sku_id,
        "weight_grams": weight_grams,
        "unit_weight_grams": unit_weight,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": location
    }

def run_mock_publisher(interval_sec: int = 5, mismatch_rate: float = 0.20):
    """
    Continually publishes telemetry payloads.
    """
    client = mqtt.Client()
    
    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

    logger.info(f"Mock publisher connecting to broker at {settings.mqtt_broker}:{settings.mqtt_port}...")
    try:
        client.connect(settings.mqtt_broker, settings.mqtt_port, 60)
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return

    client.loop_start()

    # Pre-defined demo sensors & SKUs mapping
    sensors = [
        {"id": "SHELF-A1", "sku": "SKU-9902", "loc": "WH-01-Aisle3"},
        {"id": "SHELF-B4", "sku": "SKU-1234", "loc": "WH-01-Aisle5"},
        {"id": "SHELF-C2", "sku": "SKU-4567", "loc": "WH-02-Aisle1"},
        {"id": "SHELF-D7", "sku": "SKU-8890", "loc": "WH-02-Aisle4"},
    ]

    logger.info(f"Publisher started. Emitting telemetry every {interval_sec} seconds...")
    try:
        while True:
            # Pick a random sensor
            sensor = random.choice(sensors)
            # Roll for discrepancy
            match_erp = random.random() > mismatch_rate
            
            payload = generate_mock_payload(sensor["id"], sensor["sku"], sensor["loc"], match_erp)
            topic = f"{settings.mqtt_topic_prefix}/{sensor['id']}"
            
            client.publish(topic, json.dumps(payload))
            logger.info(f"Published to {topic} -> {payload['weight_grams']:.1f}g ({round(payload['weight_grams']/payload['unit_weight_grams'])} units)")
            
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        logger.info("Stopping mock publisher...")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    run_mock_publisher()
