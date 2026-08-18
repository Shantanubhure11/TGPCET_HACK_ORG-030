"""
Dynamic Reorder Point (ROP) Calculation.
ROP = d̄L + Z√(Lσd² + d̄²σL²)
    = Lead-Time Demand + Safety Stock
"""
import numpy as np
from inventory_engine.safety_stock import calculate_safety_stock


def calculate_rop(
    mean_daily_demand: float,   # d̄ — from P50 forecast
    demand_std: float,          # σd
    mean_lead_time: float,      # L (days)
    lead_time_std: float,       # σL (days)
    service_level: float = 0.95,
) -> dict:
    """
    Dynamic Reorder Point.

    ROP = d̄ × L + Safety Stock

    Args:
        mean_daily_demand: Average daily demand (P50 forecast)
        demand_std:        Daily demand std dev (from (P90-P10)/4 or historical)
        mean_lead_time:    Mean lead time in days
        lead_time_std:     Lead time std dev
        service_level:     Target service level (0.90, 0.95, 0.99)

    Returns:
        dict with rop, safety_stock, lead_time_demand, and all components
    """
    # Lead-time demand
    lead_time_demand = mean_daily_demand * mean_lead_time

    # Safety stock
    ss_result = calculate_safety_stock(
        mean_daily_demand=mean_daily_demand,
        demand_std=demand_std,
        mean_lead_time=mean_lead_time,
        lead_time_std=lead_time_std,
        service_level=service_level,
    )

    safety_stock = ss_result["safety_stock"]
    rop = lead_time_demand + safety_stock

    return {
        "rop": round(float(rop), 2),
        "safety_stock": safety_stock,
        "lead_time_demand": round(float(lead_time_demand), 2),
        "mean_daily_demand": round(float(mean_daily_demand), 2),
        "mean_lead_time": mean_lead_time,
        "z_factor": ss_result["z_factor"],
        "service_level": service_level,
    }


def calculate_days_of_inventory(
    available_stock: float,
    mean_daily_demand: float,
) -> float:
    """Days of inventory remaining at current demand rate."""
    if mean_daily_demand <= 0:
        return float("inf")
    return round(float(available_stock) / float(mean_daily_demand), 1)


def calculate_stockout_date(
    available_stock: float,
    mean_daily_demand: float,
    from_date=None,
) -> str:
    """Projected date when stock will reach zero."""
    from datetime import date, timedelta
    from_date = from_date or date.today()
    if mean_daily_demand <= 0:
        return "Never"
    days_until_stockout = available_stock / mean_daily_demand
    stockout_date = from_date + timedelta(days=int(days_until_stockout))
    return stockout_date.isoformat()


def get_stock_status(
    available_stock: float,
    rop: float,
    safety_stock: float,
    stockout_probability: float = 0.0,
) -> str:
    """
    Classify inventory health:
    GREEN  = well stocked (above ROP)
    YELLOW = approaching ROP
    RED    = below ROP (order needed)
    """
    if stockout_probability >= 0.30:
        return "RED"
    elif available_stock <= safety_stock:
        return "RED"
    elif available_stock <= rop:
        return "YELLOW"
    else:
        return "GREEN"
