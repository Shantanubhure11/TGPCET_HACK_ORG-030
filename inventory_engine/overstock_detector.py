"""
Overstock Detection logic.
Identifies and explains overstock risk based on Days of Inventory (DOI),
inventory levels vs forecast, capacity, and low demand.
"""
from typing import Dict, Optional

def detect_overstock(
    physical_stock: float,
    available_stock: float,
    mean_daily_demand: float,
    rop: float,
    capacity: int,
    doi_threshold: int = 90,
    excess_multiplier: float = 2.0,
    low_demand_threshold: float = 5.0,
) -> dict:
    """
    Evaluate if an item is overstocked and generate explanatory reasoning.

    Args:
        physical_stock: Total stock physically in warehouse
        available_stock: Stock available for new orders (physical - allocated)
        mean_daily_demand: Expected daily sales (from ML model)
        rop: Reorder point
        capacity: Maximum shelf capacity in warehouse
        doi_threshold: Days of Inventory above which we flag overstock (default 90)
        excess_multiplier: Threshold multiplier of stock vs ROP/demand (default 2x)
        low_demand_threshold: Daily demand limit for "low demand" flagging

    Returns:
        dict: {
            "is_overstocked": bool,
            "overstock_qty": float,
            "days_of_inventory": float,
            "status": str,          # OVERSTOCK | OK
            "reason": str,
            "metric_details": dict
        }
    """
    days_of_inventory = float('inf')
    if mean_daily_demand > 0:
        days_of_inventory = available_stock / mean_daily_demand

    is_overstocked = False
    overstock_qty = 0.0
    reasons = []

    # Rule 1: DOI exceeds threshold (e.g. more than 90 days of supply)
    if days_of_inventory > doi_threshold and mean_daily_demand > 0:
        is_overstocked = True
        # Overstock quantity is whatever exceeds the threshold target (e.g. 30 days of inventory is target)
        target_stock = mean_daily_demand * 30.0
        overstock_qty = max(0.0, available_stock - target_stock)
        reasons.append(f"Days of Inventory ({days_of_inventory:.1f}) exceeds threshold of {doi_threshold} days.")

    # Rule 2: Stock exceeds warehouse capacity limit
    if physical_stock > capacity:
        is_overstocked = True
        capacity_excess = physical_stock - capacity
        overstock_qty = max(overstock_qty, capacity_excess)
        reasons.append(f"Physical stock ({physical_stock:.1f}) exceeds warehouse capacity limit of {capacity}.")

    # Rule 3: Available stock is extremely high relative to ROP
    if rop > 0 and available_stock > (rop * excess_multiplier):
        is_overstocked = True
        rop_excess = available_stock - (rop * excess_multiplier)
        overstock_qty = max(overstock_qty, rop_excess)
        reasons.append(f"Available stock ({available_stock:.1f}) is more than {excess_multiplier}x the Reorder Point ({rop:.1f}).")

    # Rule 4: High stock with extremely low daily demand
    if mean_daily_demand < low_demand_threshold and available_stock > 100 and mean_daily_demand > 0:
        # If daily demand is very slow, but we hold a large static batch
        if days_of_inventory > 120:
            is_overstocked = True
            reasons.append(f"Very low daily demand ({mean_daily_demand:.2f} units/day) with high available inventory.")

    reason_str = " ".join(reasons) if is_overstocked else "Inventory level is within healthy bounds."
    status = "OVERSTOCK" if is_overstocked else "OK"

    return {
        "is_overstocked": is_overstocked,
        "overstock_qty": round(overstock_qty, 2),
        "days_of_inventory": round(days_of_inventory, 1) if days_of_inventory != float('inf') else 9999.0,
        "status": status,
        "reason": reason_str,
        "metric_details": {
            "doi_threshold": doi_threshold,
            "excess_multiplier": excess_multiplier,
            "low_demand_threshold": low_demand_threshold,
            "capacity": capacity
        }
    }
