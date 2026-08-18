"""
Risk Engine — Monte Carlo stock-out probability + risk classification.
"""
import logging
from typing import Optional

import numpy as np

from erp_backend.config import RISK_THRESHOLDS

logger = logging.getLogger(__name__)


def calculate_stockout_probability(
    initial_inventory: float,
    mean_daily_demand: float,
    demand_std: float,
    mean_lead_time: float,
    lead_time_std: float,
    num_simulations: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Monte Carlo simulation to estimate P(Stockout) over the replenishment lead time.

    For each simulation:
    1. Sample a lead time from LogNormal(mean, std)
    2. Sample daily demands from Normal(mean, std) for that many days
    3. Check if cumulative demand exceeds initial_inventory

    Returns:
        {stockout_probability, risk_level, simulations, percentiles}
    """
    rng = np.random.default_rng(seed)

    # Clip inputs
    initial_inventory = max(0.0, float(initial_inventory))
    mean_daily_demand = max(0.0, float(mean_daily_demand))
    demand_std = max(0.0, float(demand_std))
    mean_lead_time = max(0.1, float(mean_lead_time))
    lead_time_std = max(0.0, float(lead_time_std))

    # LogNormal parameters
    if lead_time_std > 0:
        mu = np.log(mean_lead_time ** 2 / np.sqrt(lead_time_std ** 2 + mean_lead_time ** 2))
        sigma = np.sqrt(np.log(1 + (lead_time_std / mean_lead_time) ** 2))
    else:
        mu = np.log(mean_lead_time)
        sigma = 0.01

    stockout_count = 0
    lead_time_demands = []

    for _ in range(num_simulations):
        # Sample lead time (days)
        lt = max(1, round(rng.lognormal(mu, sigma)))

        # Sample daily demands
        daily_demands = rng.normal(mean_daily_demand, demand_std, lt)
        daily_demands = np.clip(daily_demands, 0, None)
        cumulative_demand = daily_demands.sum()
        lead_time_demands.append(cumulative_demand)

        if initial_inventory < cumulative_demand:
            stockout_count += 1

    p_stockout = stockout_count / num_simulations
    ltd_array = np.array(lead_time_demands)

    risk_level = classify_risk(p_stockout)

    return {
        "stockout_probability": round(p_stockout, 4),
        "risk_level": risk_level,
        "simulations": num_simulations,
        "ltd_p10": round(float(np.percentile(ltd_array, 10)), 2),
        "ltd_p50": round(float(np.percentile(ltd_array, 50)), 2),
        "ltd_p90": round(float(np.percentile(ltd_array, 90)), 2),
    }


def classify_risk(p_stockout: float) -> str:
    """
    Map stock-out probability to risk level.
    Thresholds are configurable via config.py.
    """
    if p_stockout >= RISK_THRESHOLDS["CRITICAL"]:
        return "CRITICAL"
    elif p_stockout >= RISK_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif p_stockout >= RISK_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "LOW"


def risk_color(risk_level: str) -> str:
    """Map risk level to display color."""
    return {
        "CRITICAL": "#FF4444",
        "HIGH": "#FF8C00",
        "MEDIUM": "#FFD700",
        "LOW": "#00C851",
    }.get(risk_level, "#CCCCCC")


def batch_risk_assessment(
    inventory_items: list,          # List of dicts with sku, stock, demand stats
    num_simulations: int = 500,
) -> list:
    """Run risk assessment for multiple SKUs."""
    results = []
    for item in inventory_items:
        try:
            risk = calculate_stockout_probability(
                initial_inventory=item.get("available_stock", 0),
                mean_daily_demand=item.get("mean_daily_demand", 0),
                demand_std=item.get("demand_std", 0),
                mean_lead_time=item.get("mean_lead_time", 3),
                lead_time_std=item.get("lead_time_std", 0.5),
                num_simulations=num_simulations,
            )
            results.append({**item, **risk})
        except Exception as e:
            logger.error(f"Risk calc failed for {item.get('sku_id')}: {e}")
            results.append({**item, "stockout_probability": 0, "risk_level": "UNKNOWN"})
    return results
