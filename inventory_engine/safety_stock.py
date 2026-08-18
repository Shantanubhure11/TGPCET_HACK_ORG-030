"""
Dynamic Safety Stock Calculation.
SS = Z√(Lσd² + d̄²σL²)
"""
import numpy as np
from erp_backend.config import Z_FACTORS


def calculate_safety_stock(
    mean_daily_demand: float,   # d̄
    demand_std: float,          # σd
    mean_lead_time: float,      # L (days)
    lead_time_std: float,       # σL (days)
    service_level: float = 0.95,
) -> dict:
    """
    Dynamic Safety Stock formula from the PRD.

    SS = Z × √(L × σd² + d̄² × σL²)

    Args:
        mean_daily_demand: Average daily demand (from P50 forecast)
        demand_std:        Std dev of daily demand
        mean_lead_time:    Average supplier lead time in days
        lead_time_std:     Std dev of supplier lead time in days
        service_level:     Target service level (0.90, 0.95, 0.99)

    Returns:
        dict with safety_stock, z_factor, service_level
    """
    z = _get_z_factor(service_level)

    # Variance components
    demand_variance_component = mean_lead_time * (demand_std ** 2)
    lead_time_variance_component = (mean_daily_demand ** 2) * (lead_time_std ** 2)
    combined_variance = demand_variance_component + lead_time_variance_component

    safety_stock = z * np.sqrt(max(combined_variance, 0))

    return {
        "safety_stock": round(float(safety_stock), 2),
        "z_factor": z,
        "service_level": service_level,
        "demand_variance_component": round(float(demand_variance_component), 4),
        "lead_time_variance_component": round(float(lead_time_variance_component), 4),
    }


def _get_z_factor(service_level: float) -> float:
    """Look up Z-factor for the given service level."""
    # Support both 0.95 and 95 formats
    key = service_level if service_level <= 1 else service_level / 100
    # Round to nearest standard
    for sl in [0.99, 0.95, 0.90]:
        if key >= sl:
            return Z_FACTORS[sl]
    return Z_FACTORS[0.90]


def explain_safety_stock(result: dict) -> str:
    """Generate human-readable explanation of the safety stock calculation."""
    ss = result["safety_stock"]
    z = result["z_factor"]
    sl = result["service_level"]
    sl_pct = sl * 100 if sl <= 1 else sl
    return (
        f"Safety Stock = {ss:.0f} units "
        f"(Z={z} for {sl_pct:.0f}% service level). "
        f"Accounts for both demand variability and lead-time variability."
    )
