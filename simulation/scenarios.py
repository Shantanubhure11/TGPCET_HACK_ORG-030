"""
What-If Scenario comparisons.
Runs baseline and scenario simulations side-by-side,
identifying delta parameters and cost/service impacts.
"""
from typing import Dict
from simulation.monte_carlo import run_monte_carlo

def run_scenario_comparison(
    baseline_config: dict,
    scenario_config: dict,
    num_runs: int = 100,
    horizon_days: int = 90,
    seed: int = 42
) -> dict:
    """
    Run baseline and scenario simulations, and compute deltas.
    """
    # Ensure scenario name is set
    baseline_config["scenario_name"] = baseline_config.get("scenario_name", "baseline")
    scenario_config["scenario_name"] = scenario_config.get("scenario_name", "what_if_scenario")

    # Run Monte Carlo for both
    baseline_res = run_monte_carlo(baseline_config, num_runs, horizon_days, seed)
    scenario_res = run_monte_carlo(scenario_config, num_runs, horizon_days, seed)

    # Compute deltas (Scenario - Baseline)
    delta_stockout_probability = scenario_res["stockout_probability"] - baseline_res["stockout_probability"]
    delta_total_cost = scenario_res["total_cost"] - baseline_res["total_cost"]
    delta_avg_inventory = scenario_res["avg_inventory"] - baseline_res["avg_inventory"]
    delta_service_level = scenario_res["service_level_achieved"] - baseline_res["service_level_achieved"]

    # Identify parameter differences
    changes = {}
    param_keys = [
        "rop", "safety_stock", "recommended_qty", "mean_lead_time",
        "lead_time_std", "supplier_reliability", "demand_multiplier"
    ]
    for key in param_keys:
        val_base = baseline_config.get(key)
        val_scen = scenario_config.get(key)
        if val_base != val_scen:
            changes[key] = {
                "baseline": val_base,
                "scenario": val_scen
            }

    return {
        "baseline": baseline_res,
        "scenario": scenario_res,
        "changes": changes,
        "delta_stockout_probability": round(float(delta_stockout_probability), 4),
        "delta_total_cost": round(float(delta_total_cost), 2),
        "delta_avg_inventory": round(float(delta_avg_inventory), 2),
        "delta_service_level": round(float(delta_service_level), 4)
    }
