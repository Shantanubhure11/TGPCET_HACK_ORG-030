"""
Unit tests for the Inventory Optimization Engine (ROP, Safety Stock, Risk, Overstock).
"""
import pytest
from inventory_engine.safety_stock import calculate_safety_stock
from inventory_engine.reorder_point import calculate_rop, calculate_days_of_inventory, get_stock_status
from inventory_engine.risk_engine import calculate_stockout_probability
from inventory_engine.overstock_detector import detect_overstock

def test_safety_stock_calculation():
    """Verify dynamic safety stock formula gives expected values."""
    res = calculate_safety_stock(
        mean_daily_demand=10.0,
        demand_std=2.0,
        mean_lead_time=4.0,
        lead_time_std=0.5,
        service_level=0.95
    )
    
    # ROP Safety Stock = 1.65 * sqrt(4 * 2^2 + 10^2 * 0.5^2)
    #                  = 1.65 * sqrt(16 + 25)
    #                  = 1.65 * sqrt(41)
    #                  = 1.65 * 6.403 = 10.56
    assert "safety_stock" in res
    assert res["safety_stock"] == pytest.approx(10.56, abs=0.1)

def test_rop_calculation():
    """Verify reorder point calculation includes safety stock."""
    res = calculate_rop(
        mean_daily_demand=10.0,
        demand_std=2.0,
        mean_lead_time=4.0,
        lead_time_std=0.5,
        service_level=0.95
    )
    # ROP = LTD (10*4=40) + SS (10.56) = 50.56
    assert res["lead_time_demand"] == 40.0
    assert res["rop"] == pytest.approx(50.56, abs=0.1)

def test_days_of_inventory():
    """Verify daily demand coverage calculation."""
    assert calculate_days_of_inventory(available_stock=100.0, mean_daily_demand=10.0) == 10.0
    assert calculate_days_of_inventory(available_stock=50.0, mean_daily_demand=0.0) == float('inf')

def test_stock_status_classification():
    """Verify stock status labels."""
    # Stock healthy (available stock 200 > ROP 100)
    assert get_stock_status(200.0, 100.0, 40.0) == "GREEN"
    # Stock critical (available stock 30 <= Safety Stock 40)
    assert get_stock_status(30.0, 100.0, 40.0) == "RED"
    # Stock warning (between SS and ROP)
    assert get_stock_status(60.0, 100.0, 40.0) == "YELLOW"

def test_monte_carlo_stockout_probability():
    """Verify risk simulation yields correct probability boundaries."""
    res = calculate_stockout_probability(
        initial_inventory=50.0,
        mean_daily_demand=10.0,
        demand_std=1.0,
        mean_lead_time=3.0,
        lead_time_std=0.1,
        num_simulations=100
    )
    # Stockout prob should be extremely low since stock (50) is much higher than lead time demand (30)
    assert res["stockout_probability"] < 0.05
    assert res["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_overstock_detection():
    """Verify overstock alerts."""
    res = detect_overstock(
        physical_stock=1000.0,
        available_stock=1000.0,
        mean_daily_demand=5.0,
        rop=50.0,
        capacity=1200,
        doi_threshold=90
    )
    # DOI is 200 days, should trigger overstock alert
    assert res["is_overstocked"] is True
    assert res["status"] == "OVERSTOCK"
