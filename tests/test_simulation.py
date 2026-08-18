"""
Unit tests for the Supply Chain Digital Twin SimPy simulation engine.
"""
import pytest
import simpy
from simulation.warehouse_sim import SupplyChainSimulation
from simulation.monte_carlo import run_monte_carlo
from simulation.scenarios import run_scenario_comparison

@pytest.fixture
def base_sim_config():
    """Generates standard parameters configuration."""
    return {
        "sku_id": "SKU-9902",
        "initial_inventory": 100.0,
        "rop": 60.0,
        "safety_stock": 30.0,
        "recommended_qty": 200,
        "p10_demand": 8.0,
        "p50_demand": 12.0,
        "p90_demand": 16.0,
        "mean_lead_time": 3.0,
        "lead_time_std": 0.5,
        "supplier_reliability": 0.95,
        "holding_cost_per_unit_day": 0.05,
        "shortage_cost_per_unit_day": 1.0,
        "order_cost": 50.0
    }

def test_single_run_simulation(base_sim_config):
    """Verify single replenishment cycle simulation run."""
    env = simpy.Environment()
    sim = SupplyChainSimulation(env, base_sim_config, seed=42)
    results = sim.run(horizon_days=30)
    
    assert "avg_inventory" in results
    assert "total_cost" in results
    assert "service_level_achieved" in results
    assert len(results["inventory_history"]) > 1

def test_monte_carlo_simulation(base_sim_config):
    """Verify multi-run stochastic Monte Carlo output metrics."""
    res = run_monte_carlo(base_sim_config, num_runs=10, horizon_days=30, base_seed=42)
    
    assert res["status"] == "COMPLETED"
    assert "avg_inventory" in res
    assert len(res["inventory_curve"]) == 31 # day 0 to 30

def test_scenario_comparison(base_sim_config):
    """Verify Delta calculation between baseline and delayed supplier scenario."""
    delayed_config = base_sim_config.copy()
    # Double the supplier lead time
    delayed_config["mean_lead_time"] = 6.0
    
    comp = run_scenario_comparison(
        baseline_config=base_sim_config,
        scenario_config=delayed_config,
        num_runs=10,
        horizon_days=30
    )
    
    assert "delta_stockout_probability" in comp
    assert "delta_total_cost" in comp
    # Delayed lead time should increase stockout probability and shortages cost
    assert comp["scenario"]["stockout_probability"] >= comp["baseline"]["stockout_probability"]
