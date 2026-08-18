"""
Inventory Service.
Handles stock lookups, adjustments, ledgers, health checks, and calculations.
"""
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from erp_backend.models.inventory import Inventory
from erp_backend.models.inventory_ledger import InventoryLedger
from erp_backend.models.item import Item
from erp_backend.models.supplier import Supplier
from erp_backend.schemas.inventory import InventoryAdjust

# Math calculators
from inventory_engine.safety_stock import calculate_safety_stock
from inventory_engine.reorder_point import (
    calculate_rop, calculate_days_of_inventory, get_stock_status
)
from inventory_engine.risk_engine import calculate_stockout_probability
from erp_backend.services.demand_forecasting_service import get_forecast_for_sku

logger = logging.getLogger(__name__)

def get_inventory_status_by_sku(db: Session, sku_id: str, warehouse_id: str) -> dict:
    """
    Retrieves full inventory details for a SKU in a warehouse,
    recalculating safety stock, ROP, and stockout probability on-the-fly.
    """
    inv = db.query(Inventory).filter(
        Inventory.sku_id == sku_id,
        Inventory.warehouse_id == warehouse_id
    ).first()

    if not inv:
        return {}

    item = db.query(Item).filter(Item.sku_id == sku_id).first()
    supplier = db.query(Supplier).filter(Supplier.supplier_id == item.supplier_id).first() if item else None

    # Default supplier parameters
    lead_time_mean = supplier.avg_lead_time if supplier else 3.0
    lead_time_std = supplier.lead_time_std if supplier else 0.5

    # 1. Fetch forecast metrics to get mean daily demand and standard deviation
    forecast_res = get_forecast_for_sku(db, sku_id, horizon=30)
    forecast_points = forecast_res["forecast"]
    
    if forecast_points:
        p50_demands = [p["p50"] for p in forecast_points]
        mean_demand = float(sum(p50_demands) / len(p50_demands))
        # Std dev of demand
        demand_std = float(max(1.0, float(np.std(p50_demands))))
    else:
        mean_demand = 10.0
        demand_std = 2.0

    # 2. Recalculate dynamic ROP and Safety Stock
    rop_res = calculate_rop(
        mean_daily_demand=mean_demand,
        demand_std=demand_std,
        mean_lead_time=lead_time_mean,
        lead_time_std=lead_time_std,
        service_level=0.95
    )
    
    safety_stock = rop_res["safety_stock"]
    rop = rop_res["rop"]

    # Sync back to database cache
    inv.safety_stock = safety_stock
    inv.rop = rop
    db.commit()

    # 3. Calculate stockout probability using Monte Carlo
    available_stock = float(inv.physical_stock) - float(inv.allocated_stock)
    risk_res = calculate_stockout_probability(
        initial_inventory=available_stock,
        mean_daily_demand=mean_demand,
        demand_std=demand_std,
        mean_lead_time=lead_time_mean,
        lead_time_std=lead_time_std,
        num_simulations=500
    )

    stockout_prob = risk_res["stockout_probability"]
    risk_level = risk_res["risk_level"]

    # 4. Calculate days of inventory
    doi = calculate_days_of_inventory(available_stock, mean_demand)
    
    # 5. Get traffic status
    stock_status = get_stock_status(available_stock, rop, safety_stock, stockout_prob)

    return {
        "inventory_id": inv.inventory_id,
        "sku_id": inv.sku_id,
        "sku_name": item.name if item else "Unknown",
        "warehouse_id": inv.warehouse_id,
        "physical_stock": float(inv.physical_stock),
        "allocated_stock": float(inv.allocated_stock),
        "available_stock": available_stock,
        "incoming_stock": float(inv.incoming_stock),
        "safety_stock": safety_stock,
        "rop": rop,
        "days_of_inventory": doi,
        "stock_status": stock_status,
        "stockout_probability": stockout_prob,
        "risk_level": risk_level,
        "last_counted_at": inv.last_counted_at,
        "updated_at": inv.updated_at
    }

def adjust_inventory_stock(db: Session, adj: InventoryAdjust) -> dict:
    """
    Performs stock adjustment and records transaction in ledger.
    """
    inv = db.query(Inventory).filter(
        Inventory.sku_id == adj.sku_id,
        Inventory.warehouse_id == adj.warehouse_id
    ).first()

    if not inv:
        # Create inventory row if not exists
        inv = Inventory(
            sku_id=adj.sku_id,
            warehouse_id=adj.warehouse_id,
            physical_stock=0.0,
            allocated_stock=0.0,
            incoming_stock=0.0,
            safety_stock=0.0,
            rop=0.0
        )
        db.add(inv)
        db.flush()

    previous_balance = float(inv.physical_stock)
    new_balance = previous_balance + adj.qty_change

    # Overwrite physical stock
    inv.physical_stock = new_balance
    inv.last_counted_at = datetime.utcnow()

    # Log to Ledger (Immutable audit trail)
    ledger = InventoryLedger(
        sku_id=adj.sku_id,
        warehouse_id=adj.warehouse_id,
        transaction_type=adj.reason.upper(),
        reference_id=adj.notes,
        qty_change=adj.qty_change,
        previous_balance=previous_balance,
        new_balance=new_balance,
        timestamp=datetime.utcnow(),
        user_id=adj.user_id,
        notes=adj.notes
    )
    db.add(ledger)
    db.commit()

    return {
        "status": "success",
        "sku_id": adj.sku_id,
        "warehouse_id": adj.warehouse_id,
        "previous_balance": previous_balance,
        "new_balance": new_balance,
        "qty_change": adj.qty_change
    }
import numpy as np
