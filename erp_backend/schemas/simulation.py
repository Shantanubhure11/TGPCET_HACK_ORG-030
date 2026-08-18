"""Pydantic schemas for Supply Chain Simulation."""
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    scenario_name: str = "baseline"
    sku_id: str
    lead_time_mean: float = Field(3.0, ge=0.1, le=60)
    lead_time_std: float = Field(0.5, ge=0, le=10)
    demand_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    supplier_reliability_pct: float = Field(95.0, ge=0, le=100)
    service_level: float = Field(95.0, ge=80, le=99.9)
    num_runs: int = Field(100, ge=10, le=1000)
    horizon_days: int = Field(90, ge=7, le=365)


class InventoryPoint(BaseModel):
    day: int
    avg_inventory: float
    p10_inventory: float
    p90_inventory: float


class SimulationResult(BaseModel):
    simulation_id: str
    scenario_name: str
    sku_id: str
    status: str                         # COMPLETED | RUNNING | FAILED

    # Aggregate results
    avg_inventory: Optional[float] = None
    max_inventory: Optional[float] = None
    min_inventory: Optional[float] = None
    stockout_events: Optional[int] = None
    stockout_probability: Optional[float] = None
    service_level_achieved: Optional[float] = None
    total_cost: Optional[float] = None
    holding_cost: Optional[float] = None
    shortage_cost: Optional[float] = None
    ordering_cost: Optional[float] = None

    # Dynamic ROP results
    rop: Optional[float] = None
    safety_stock: Optional[float] = None
    recommended_po_qty: Optional[int] = None

    # Time series (downsampled)
    inventory_curve: Optional[List[InventoryPoint]] = None

    # Metadata
    num_runs: Optional[int] = None
    execution_time_sec: Optional[float] = None
    parameters: Optional[dict] = None


class WhatIfComparison(BaseModel):
    baseline: SimulationResult
    scenario: SimulationResult
    changes: Dict[str, dict]            # parameter_name → {baseline: x, scenario: y}
    delta_stockout_probability: Optional[float] = None
    delta_total_cost: Optional[float] = None
    delta_avg_inventory: Optional[float] = None
