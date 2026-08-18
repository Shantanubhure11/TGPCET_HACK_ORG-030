"""
IoT Telemetry Simulator Script.
Generates mock telemetry readings and sends them to the backend server.
Supports direct HTTP POST submission (no MQTT broker needed) or MQTT publish.
"""
import sys
import os
import time
import random
import requests
import argparse
from datetime import datetime

# Insert workspace root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from erp_backend.config import get_settings

settings = get_settings()

def get_arg_parser():
    parser = argparse.ArgumentParser(description="IoT Telemetry Simulator for Supply Chain Twin")
    parser.add_argument("--mode", choices=["http", "mqtt"], default="http", help="HTTP post vs MQTT publish")
    parser.add_argument("--interval", type=int, default=5, help="Interval in seconds between sensor readings")
    parser.add_argument("--discrepancy-rate", type=float, default=0.20, help="Probability of inducing a stock mismatch")
    return parser

def generate_telemetry_reading(sensor_id: str, sku_id: str, location: str, induce_discrepancy: bool) -> dict:
    unit_weight = 150.0  # grams
    expected_qty = random.randint(30, 80)
    
    if induce_discrepancy:
        # Induce weight mismatch (e.g. stock missing)
        actual_qty = expected_qty - random.choice([15, 20, 30])
        actual_qty = max(2, actual_qty)
    else:
        actual_qty = expected_qty
        
    weight = actual_qty * unit_weight
    
    return {
        "sensor_id": sensor_id,
        "sku_id": sku_id,
        "weight_grams": weight,
        "unit_weight_grams": unit_weight,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": location
    }

def run_http_simulator(interval: int, rate: float):
    url = f"{settings.backend_url}/api/iot/telemetry"
    print(f"Starting HTTP Telemetry Simulator. Submitting directly to {url}...")
    
    sensors = [
        {"id": "SENSOR-IC-3", "sku": "SKU-9902", "loc": "Aisle 3, Row B"},
        {"id": "SENSOR-OLED-5", "sku": "SKU-1234", "loc": "Aisle 5, Row A"},
        {"id": "SENSOR-BOX-45", "sku": "SKU-4567", "loc": "Aisle 1, Row C"},
        {"id": "SENSOR-PUMP-8", "sku": "SKU-8890", "loc": "Aisle 4, Row F"}
    ]
    
    try:
        while True:
            sensor = random.choice(sensors)
            induce = random.random() < rate
            payload = generate_telemetry_reading(sensor["id"], sensor["sku"], sensor["loc"], induce)
            
            try:
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    flag = "ALERT!" if data.get("alert_flag") else "OK"
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Submitted {sensor['id']} -> {payload['weight_grams']:.0f}g ({int(payload['weight_grams']/payload['unit_weight_grams'])} units). Status: {flag} (Diff: {data.get('discrepancy_pct') or 0.0}%)")
                else:
                    print(f"Submission failed: {res.text}")
            except Exception as e:
                print(f"Connection error to backend: {e}")
                
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nHTTP Telemetry Simulator stopped.")

def run_mqtt_simulator(interval: int, rate: float):
    # Delegate to the paho-mqtt listener/publisher
    from iot.mqtt_publisher import run_mock_publisher
    print("Delegating to MQTT Publisher module...")
    run_mock_publisher(interval_sec=interval, mismatch_rate=rate)

def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    
    if args.mode == "http":
        run_http_simulator(args.interval, args.discrepancy_rate)
    else:
        run_mqtt_simulator(args.interval, args.discrepancy_rate)

if __name__ == "__main__":
    main()
