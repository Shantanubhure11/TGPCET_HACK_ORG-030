"""
Dashboard API Utility Connector.
Queries the FastAPI backend server and provides offline fallback mock data
in case the backend is not running, ensuring a bulletproof hackathon demo.
"""
import logging
import requests
import streamlit as st
from erp_backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BACKEND_URL = settings.backend_url

def fetch_api(path: str, method: str = "GET", params: dict = None, json_data: dict = None) -> dict:
    """Sends a request to the backend API. Falls back to mock data if connection fails."""
    url = f"{BACKEND_URL}{path}"
    try:
        if method == "GET":
            res = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            res = requests.post(url, json=json_data, timeout=5)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"API Error {res.status_code} for path {path}: {res.text}")
    except Exception as e:
        logger.warning(f"Connection failed to backend at {url}. Error: {e}. Generating fallback mock data.")
    
    # Generate mock fallbacks to keep the Streamlit app fully functional
    return generate_mock_fallback(path, params, json_data)

def generate_mock_fallback(path: str, params: dict = None, json_data: dict = None):
    """Generates mock data mirroring the expected backend response schemas."""
    import random
    from datetime import date, timedelta

    if "/api/inventory/list" in path:
        return [
            {
                "inventory_id": 1,
                "sku_id": "SKU-9902",
                "sku_name": "Precision micro-controller IC",
                "warehouse_id": "WH-01",
                "physical_stock": 140.0,
                "allocated_stock": 35.0,
                "available_stock": 105.0,
                "incoming_stock": 200.0,
                "safety_stock": 150.0,
                "rop": 280.0,
                "days_of_inventory": 8.4,
                "stock_status": "YELLOW",
                "stockout_probability": 0.22,
                "risk_level": "HIGH",
                "last_counted_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "inventory_id": 2,
                "sku_id": "SKU-1234",
                "sku_name": "OLED Display Panel 5.5 inch",
                "warehouse_id": "WH-01",
                "physical_stock": 450.0,
                "allocated_stock": 20.0,
                "available_stock": 430.0,
                "incoming_stock": 0.0,
                "safety_stock": 100.0,
                "rop": 180.0,
                "days_of_inventory": 25.1,
                "stock_status": "GREEN",
                "stockout_probability": 0.02,
                "risk_level": "LOW",
                "last_counted_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "inventory_id": 3,
                "sku_id": "SKU-4567",
                "sku_name": "Reinforced Cardboard Box 12x12x12",
                "warehouse_id": "WH-01",
                "physical_stock": 25.0,
                "allocated_stock": 5.0,
                "available_stock": 20.0,
                "incoming_stock": 500.0,
                "safety_stock": 300.0,
                "rop": 550.0,
                "days_of_inventory": 0.5,
                "stock_status": "RED",
                "stockout_probability": 0.88,
                "risk_level": "CRITICAL",
                "last_counted_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]

    elif "/api/forecast/demand" in path:
        sku_id = params.get("sku_id") if params else "SKU-9902"
        horizon = params.get("horizon", 30) if params else 30
        
        start_date = date.today()
        forecast = []
        base = 15.0 if sku_id == "SKU-9902" else 25.0
        
        for i in range(horizon):
            f_date = start_date + timedelta(days=i)
            p50 = base + random.uniform(-2, 2) + (5.0 if f_date.weekday() >= 5 else 0.0)
            forecast.append({
                "forecast_date": f_date.isoformat(),
                "p10": max(0.0, p50 * 0.7),
                "p50": p50,
                "p90": p50 * 1.3,
                "actual": None
            })
            
        return {
            "sku_id": sku_id,
            "run_date": date.today().isoformat(),
            "horizon": horizon,
            "forecast": forecast,
            "model_metrics": {"wape": 0.142, "rmse": 4.8},
            "model_version": "fallback_model_v1.0"
        }

    elif "/api/purchases/recommendations" in path:
        return [
            {
                "recommendation_id": "rec-001",
                "sku_id": "SKU-9902",
                "sku_name": "Precision micro-controller IC",
                "supplier_id": "SUP-001",
                "supplier_name": "Alpha Logistics & Mfg",
                "recommended_qty": 400,
                "current_stock": 140.0,
                "available_stock": 105.0,
                "incoming_stock": 200.0,
                "rop": 280.0,
                "safety_stock": 150.0,
                "lead_time_demand": 130.0,
                "target_inventory": 410.0,
                "supplier_moq": 100,
                "stockout_probability": 0.22,
                "projected_stockout_date": (date.today() + timedelta(days=8)).isoformat(),
                "urgency": "HIGH",
                "reason": "Net available stock (105.0) fell below dynamic Reorder Point (280.0). Replenishment order required to cover lead time demand.",
                "estimated_cost": 6000.0
            },
            {
                "recommendation_id": "rec-002",
                "sku_id": "SKU-4567",
                "sku_name": "Reinforced Cardboard Box 12x12x12",
                "supplier_id": "SUP-002",
                "supplier_name": "Bharat Components",
                "recommended_qty": 1000,
                "current_stock": 25.0,
                "available_stock": 20.0,
                "incoming_stock": 500.0,
                "rop": 550.0,
                "safety_stock": 300.0,
                "lead_time_demand": 250.0,
                "target_inventory": 800.0,
                "supplier_moq": 500,
                "stockout_probability": 0.88,
                "projected_stockout_date": (date.today() + timedelta(days=1)).isoformat(),
                "urgency": "CRITICAL",
                "reason": "Net available stock (20.0) is dangerously depleted. Critical risk of stockout within 24 hours.",
                "estimated_cost": 1200.0
            }
        ]

    elif "/api/suppliers" in path:
        return [
            {"supplier_id": "SUP-001", "name": "Alpha Logistics & Mfg", "avg_lead_time": 2.0, "lead_time_std": 0.3, "reliability_pct": 98.0, "moq": 100, "capacity": 5000, "created_at": "", "updated_at": ""},
            {"supplier_id": "SUP-002", "name": "Bharat Components", "avg_lead_time": 4.0, "lead_time_std": 0.8, "reliability_pct": 92.0, "moq": 500, "capacity": 10000, "created_at": "", "updated_at": ""},
            {"supplier_id": "SUP-003", "name": "Apex Global Traders", "avg_lead_time": 7.0, "lead_time_std": 1.5, "reliability_pct": 85.0, "moq": 500, "capacity": 15000, "created_at": "", "updated_at": ""}
        ]

    elif "/api/purchases/pending" in path:
        return [
            {
                "po_id": 101,
                "po_number": "PO-20260818-B41E",
                "supplier_id": "SUP-002",
                "sku_id": "SKU-4567",
                "order_qty": 500.0,
                "unit_cost": 1.20,
                "order_date": date.today().isoformat(),
                "expected_delivery": (date.today() + timedelta(days=4)).isoformat(),
                "actual_delivery": None,
                "status": "PENDING",
                "notes": "Emergency cardboard restocking",
                "created_at": datetime.now().isoformat()
            }
        ]

    elif "/api/alerts/active" in path:
        return [
            {
                "alert_id": "alt-8b4e11",
                "alert_type": "IOT_DISCREPANCY",
                "severity": "CRITICAL",
                "sku_id": "SKU-9902",
                "sensor_id": "SHELF-B04",
                "message": "IoT Inventory Discrepancy: sensor SHELF-B04 reports 30 units, but ERP records 45 units. Mismatch is 33.3%.",
                "details": {"sensor_id": "SHELF-B04", "sku_id": "SKU-9902", "detected_qty": 30.0, "erp_qty": 45.0, "discrepancy_pct": 33.3},
                "is_acknowledged": False,
                "created_at": datetime.now().isoformat()
            },
            {
                "alert_id": "alt-9241aa",
                "alert_type": "STOCKOUT",
                "severity": "CRITICAL",
                "sku_id": "SKU-4567",
                "sensor_id": None,
                "message": "Stockout Risk Critical: SKU-4567 available stock (20.0) is below safety stock limit.",
                "details": {},
                "is_acknowledged": False,
                "created_at": datetime.now().isoformat()
            }
        ]

    elif "/api/simulation/run" in path:
        sku_id = json_data.get("sku_id") if json_data else "SKU-9902"
        horizon = json_data.get("horizon_days", 90) if json_data else 90
        
        # Generate simulation curve
        curve = []
        inv = 200.0
        for d in range(horizon + 1):
            # Simulate daily drops and order receipts
            inv -= random.uniform(5, 15)
            if inv < 50:
                inv += 200.0 # replenishment receipt
            curve.append({
                "day": d,
                "avg_inventory": float(inv),
                "p10_inventory": float(inv * 0.8),
                "p90_inventory": float(inv * 1.2)
            })
            
        return {
            "simulation_id": "sim-mock101",
            "status": "COMPLETED",
            "scenario_name": json_data.get("scenario_name", "baseline") if json_data else "baseline",
            "sku_id": sku_id,
            "avg_inventory": 185.4,
            "max_inventory": 350.0,
            "min_inventory": 25.0,
            "stockout_events": 2,
            "stockout_probability": 0.022,
            "service_level_achieved": 0.978,
            "total_cost": 4200.0,
            "holding_cost": 2100.0,
            "shortage_cost": 1500.0,
            "ordering_cost": 600.0,
            "rop": 80.0,
            "safety_stock": 35.0,
            "recommended_po_qty": 200,
            "inventory_curve": curve
        }

    elif "/api/iot/logs" in path:
        return [
            {
                "log_id": 1,
                "sensor_id": "SHELF-B04",
                "sku_id": "SKU-9902",
                "sku_name": "Precision micro-controller IC",
                "calculated_quantity": 30.0,
                "erp_quantity_at_time": 45.0,
                "discrepancy_qty": 15.0,
                "discrepancy_pct": 33.3,
                "alert_flag": True,
                "alert_level": "CRITICAL",
                "timestamp": datetime.now().isoformat(),
                "location": "WH-01-Aisle3"
            }
        ]

    return {}

from datetime import datetime
