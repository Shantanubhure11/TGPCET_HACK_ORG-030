"""
Monte Carlo Simulation Wrapper.
Runs multiple stochastic warehouse simulations in parallel or sequence,
and aggregates the results (percentiles, cost distributions, service levels).
"""
import simpy
import numpy as np
from typing import List, Dict, Any
from simulation.warehouse_sim import SupplyChainSimulation

def run_monte_carlo(
    config: dict,
    num_runs: int = 100,
    horizon_days: int = 90,
    base_seed: int = 42
) -> dict:
    """
    Runs a batch of stochastic supply chain simulations and aggregates the stats.

    Returns:
        dict: Aggregated simulation metrics suitable for UI rendering and comparison.
    """
    runs_data = []
    
    # Track inventory across all simulations per day to build quantile curves
    # daily_inventories will be a matrix of shape (num_runs, horizon_days + 1)
    daily_inventories = np.zeros((num_runs, horizon_days + 1))

    for run_idx in range(num_runs):
        env = simpy.Environment()
        sim_seed = base_seed + run_idx
        sim = SupplyChainSimulation(env, config, seed=sim_seed)
        
        # Run simulation
        results = sim.run(horizon_days)
        runs_data.append(results)

        # Record daily inventory
        # Fill in inventory history array
        hist = results["inventory_history"]
        
        # Resolve time step to daily increments
        # Map time index to the closest day index
        day_stock = np.zeros(horizon_days + 1)
        # Prepopulate with initial inventory
        day_stock[0] = sim.initial_inventory
        
        # Forward fill the inventory array per day based on events
        current_inv = sim.initial_inventory
        event_idx = 0
        for day in range(horizon_days + 1):
            # Find the last inventory level before or at this day
            while event_idx < len(hist) and hist[event_idx]["time"] <= day:
                current_inv = hist[event_idx]["inventory"]
                event_idx += 1
            day_stock[day] = current_inv
            
        daily_inventories[run_idx, :] = day_stock

    # Aggregations
    avg_inventories = np.mean(daily_inventories, axis=0)
    p10_inventories = np.percentile(daily_inventories, 10, axis=0)
    p90_inventories = np.percentile(daily_inventories, 90, axis=0)

    # Convert inventory curve to list of dicts for Pydantic/JSON
    inventory_curve = []
    for day in range(horizon_days + 1):
        inventory_curve.append({
            "day": day,
            "avg_inventory": round(float(avg_inventories[day]), 2),
            "p10_inventory": round(float(p10_inventories[day]), 2),
            "p90_inventory": round(float(p90_inventories[day]), 2)
        })

    # Aggregating scalars across runs
    avg_inv = np.mean([r["avg_inventory"] for r in runs_data])
    max_inv = np.max([r["max_inventory"] for r in runs_data])
    min_inv = np.min([r["min_inventory"] for r in runs_data])
    
    avg_stockout_events = np.mean([r["stockout_events"] for r in runs_data])
    stockout_prob = np.mean([r["stockout_probability"] for r in runs_data])
    service_level = np.mean([r["service_level_achieved"] for r in runs_data])
    
    total_cost = np.mean([r["total_cost"] for r in runs_data])
    holding_cost = np.mean([r["holding_cost"] for r in runs_data])
    shortage_cost = np.mean([r["shortage_cost"] for r in runs_data])
    ordering_cost = np.mean([r["ordering_cost"] for r in runs_data])

    import uuid
    simulation_id = f"sim-{uuid.uuid4().hex[:8]}"

    return {
        "simulation_id": simulation_id,
        "status": "COMPLETED",
        "scenario_name": config.get("scenario_name", "baseline"),
        "sku_id": config.get("sku_id", ""),
        "avg_inventory": round(float(avg_inv), 2),
        "max_inventory": round(float(max_inv), 2),
        "min_inventory": round(float(min_inv), 2),
        "stockout_events": int(round(avg_stockout_events)),
        "stockout_probability": round(float(stockout_prob), 4),
        "service_level_achieved": round(float(service_level), 4),
        "total_cost": round(float(total_cost), 2),
        "holding_cost": round(float(holding_cost), 2),
        "shortage_cost": round(float(shortage_cost), 2),
        "ordering_cost": round(float(ordering_cost), 2),
        "inventory_curve": inventory_curve,
        "num_runs": num_runs,
        "parameters": {
            "initial_inventory": config.get("initial_inventory"),
            "rop": config.get("rop"),
            "safety_stock": config.get("safety_stock"),
            "recommended_qty": config.get("recommended_qty"),
            "mean_lead_time": config.get("mean_lead_time"),
            "lead_time_std": config.get("lead_time_std"),
            "supplier_reliability": config.get("supplier_reliability"),
            "demand_multiplier": config.get("demand_multiplier", 1.0)
        }
    }
