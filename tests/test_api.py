"""
FastAPI Backend Integration Endpoint Tests.
Uses TestClient to verify health checks, forecast parameters, and alert ingestion routes.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Set testing environment variables before importing main app
os.environ["DATABASE_URL"] = "sqlite:///./test_supply_chain.db"
os.environ["LOG_LEVEL"] = "WARNING"

from erp_backend.main import app
from erp_backend.database import create_all_tables, engine, Base

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Setup a clean SQLite database context for routing tests."""
    Base.metadata.create_all(bind=engine)
    
    # Pre-populate minimal mock SKU, Supplier and Warehouse
    from erp_backend.database import SessionLocal
    from erp_backend.models.item import Item
    from erp_backend.models.supplier import Supplier
    from erp_backend.models.warehouse import Warehouse
    from erp_backend.models.inventory import Inventory
    
    db = SessionLocal()
    
    # Check/insert supplier
    sup = Supplier(supplier_id="SUP-001", name="Test Supplier", avg_lead_time=2.0, lead_time_std=0.2, reliability_pct=95.0, moq=10)
    db.add(sup)
    
    # Check/insert warehouse
    wh = Warehouse(warehouse_id="WH-01", name="Test Warehouse", capacity=50000)
    db.add(wh)
    
    # Check/insert Item
    item = Item(sku_id="SKU-9902", name="Microcontroller IC", category="Electronics", unit="pcs", unit_cost=10.0, selling_price=20.0, supplier_id="SUP-001", moq=50)
    db.add(item)
    db.flush()
    
    # Check/insert Inventory
    inv = Inventory(sku_id="SKU-9902", warehouse_id="WH-01", physical_stock=100.0, allocated_stock=10.0, incoming_stock=0.0)
    db.add(inv)
    
    db.commit()
    db.close()
    
    yield
    # Cleanup database tables
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_supply_chain.db"):
        os.remove("./test_supply_chain.db")

def test_health_check_endpoint():
    """Verify health check returns 200."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_inventory_health_endpoint():
    """Verify current inventory parameters retrieve correctly."""
    res = client.get("/api/inventory/current?sku_id=SKU-9902&warehouse_id=WH-01")
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == "SKU-9902"
    assert data["available_stock"] == 90.0
    assert "stock_status" in data

def test_forecast_demand_endpoint():
    """Verify forecast endpoint queries and runs predictions."""
    res = client.get("/api/forecast/demand?sku_id=SKU-9902&horizon=7")
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == "SKU-9902"
    assert len(data["forecast"]) == 7

def test_iot_telemetry_ingest():
    """Verify IoT HTTP telemetry discrepancy processor."""
    payload = {
        "sensor_id": "SHELF-TEST",
        "sku_id": "SKU-9902",
        "weight_grams": 15000.0,      # 100 units * 150g
        "unit_weight_grams": 150.0,
        "location": "WH-01"
    }
    res = client.post("/api/iot/telemetry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["data"]["sensor_id"] == "SHELF-TEST"
