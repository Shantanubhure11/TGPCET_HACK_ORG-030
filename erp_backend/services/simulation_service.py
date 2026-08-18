"""
Simulation Service.
Resolves database SKU and supplier parameters and triggers SimPy Monte Carlo simulations.
"""
import logging
from sqlalchemy.orm import Session
from erp_backend.models.item import Item
from erp_backend.models.supplier import Supplier
from erp_backend.models.inventory import Inventory
from erp_backend.schemas.simulation import SimulationRequest
from simulation.monte_carlo import run_monte_carlo
from simulation.scenarios import run_scenario_comparison
from erp_backend.services.demand_forecasting_service import get_forecast_for_sku

logger = logging.getLogger(__name__)

def execute_monte_carlo_simulation(db: Session, req: SimulationRequest) -> dict:
    """
    Looks up stock and forecast parameters from database and runs the Monte Carlo SimPy simulation.
    """
    # 1. Fetch item and supplier details
    item = db.query(Item).filter(Item.sku_id == req.sku_id).first()
    if not item:
        raise ValueError(f"SKU {req.sku_id} not found in master data")

    supplier = db.query(Supplier).filter(Supplier.supplier_id == item.supplier_id).first()
    if not supplier:
        raise ValueError(f"Supplier for SKU {req.sku_id} not configured")

    inv = db.query(Inventory).filter(
        Inventory.sku_id == req.sku_id,
        Inventory.warehouse_id == "WH-01"
    ).first()
    initial_stock = float(inv.physical_stock) if inv else 100.0

    # 2. Get forecast quantiles
    forecast_res = get_forecast_for_sku(db, req.sku_id, horizon=req.horizon_days)
    forecast_points = forecast_res["forecast"]
    
    # Take average quantiles over the forecast period
    p10_vals = [p["p10"] for p in forecast_points] if forecast_points else [8.0]
    p50_vals = [p["p50"] for p in forecast_points] if forecast_points else [12.0]
    p90_vals = [p["p90"] for p in forecast_points] if forecast_points else [16.0]

    p10_avg = float(sum(p10_vals) / len(p10_vals)) * req.demand_multiplier
    p50_avg = float(sum(p50_vals) / len(p50_vals)) * req.demand_multiplier
    p90_avg = float(sum(p90_vals) / len(p90_vals)) * req.demand_multiplier

    # Get MOQ
    moq = supplier.moq if supplier else 100

    # 3. Create simulation config
    config = {
        "scenario_name": req.scenario_name,
        "sku_id": req.sku_id,
        "initial_inventory": initial_stock,
        "rop": float(inv.rop) if inv else 50.0,
        "safety_stock": float(inv.safety_stock) if inv else 20.0,
        "recommended_qty": max(moq, 200),
        "p10_demand": p10_avg,
        "p50_demand": p50_avg,
        "p90_demand": p90_avg,
        "mean_lead_time": req.lead_time_mean,
        "lead_time_std": req.lead_time_std,
        "supplier_reliability": req.supplier_reliability_pct / 100.0,
        "holding_cost_per_unit_day": 0.05,
        "shortage_cost_per_unit_day": 1.0,
        "order_cost": 50.0,
        "demand_multiplier": req.demand_multiplier
    }

    # 4. Trigger simulation runs
    results = run_monte_carlo(
        config=config,
        num_runs=req.num_runs,
        horizon_days=req.horizon_days
    )
    return results

def execute_whatif_comparison(db: Session, base_req: SimulationRequest, scenario_req: SimulationRequest) -> dict:
    """
    Runs both baseline and scenario simulations and returns side-by-side delta results.
    """
    baseline_res = execute_monte_carlo_simulation(db, base_req)
    
    # Run scenario
    scenario_res = execute_monte_carlo_simulation(db, scenario_req)

    delta_stockout_probability = scenario_res["stockout_probability"] - baseline_res["stockout_probability"]
    delta_total_cost = scenario_res["total_cost"] - baseline_res["total_cost"]
    delta_avg_inventory = scenario_res["avg_inventory"] - baseline_res["avg_inventory"]
    delta_service_level = scenario_res["service_level_achieved"] - baseline_res["service_level_achieved"]

    # Parameter diffs
    changes = {}
    param_keys = [
        "lead_time_mean", "lead_time_std", "demand_multiplier", "supplier_reliability_pct", "service_level"
    ]
    for key in param_keys:
        val_base = getattr(base_req, key)
        val_scen = getattr(scenario_req, key)
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
