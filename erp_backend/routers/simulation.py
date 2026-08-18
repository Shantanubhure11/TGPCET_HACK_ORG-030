"""
Simulation API Router.
Triggers stochastic SimPy supply chain digital twin simulations and compares What-If scenarios.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from erp_backend.database import get_db
from erp_backend.schemas.simulation import SimulationRequest, SimulationResult, WhatIfComparison
from erp_backend.services.simulation_service import execute_monte_carlo_simulation, execute_whatif_comparison

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/simulation", tags=["Digital Twin Simulation"])

@router.post("/run", response_model=SimulationResult)
def run_simulation(
    payload: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Triggers a SimPy discrete-event Monte Carlo simulation for a SKU.
    Executes multiple stochastic runs and aggregates the average inventory curves,
    costs, and service levels achieved.
    """
    try:
        results = execute_monte_carlo_simulation(db, payload)
        return results
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Simulation run aborted due to internal server error")

@router.post("/compare", response_model=WhatIfComparison)
def compare_scenarios(
    baseline_req: SimulationRequest,
    scenario_req: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulates baseline and a What-If scenario side-by-side.
    Returns comparison data, charts metrics, and highlights deltas in stockouts/costs.
    """
    try:
        comparison = execute_whatif_comparison(db, baseline_req, scenario_req)
        return comparison
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Scenario comparison failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Scenario comparison failed")
