"""
Procurement Recommendation Engine.
Triggers PO recommendations when inventory + incoming < ROP.
Calculates recommended order quantities respecting supplier MOQ and capacity limits.
Provides explainable reasons and urgency classification.
"""
from typing import Dict, Optional, Any
import numpy as np
from datetime import date, timedelta
from inventory_engine.risk_engine import calculate_stockout_probability
from inventory_engine.reorder_point import calculate_stockout_date

def recommend_purchase_order(
    sku_id: str,
    sku_name: str,
    supplier_id: str,
    supplier_name: str,
    current_stock: float,
    allocated_stock: float,
    incoming_stock: float,
    mean_daily_demand: float,
    demand_std: float,
    rop: float,
    safety_stock: float,
    supplier_moq: int,
    supplier_capacity: int,
    lead_time_mean: float,
    lead_time_std: float,
    service_level: float = 0.95,
    unit_cost: Optional[float] = None
) -> dict:
    """
    Generate purchase order recommendations with explainable reasoning.

    Args:
        sku_id: Product ID
        sku_name: Product Name
        supplier_id: Supplier ID
        supplier_name: Supplier Name
        current_stock: Physical stock on hand (physical_stock)
        allocated_stock: Stock reserved for sales (allocated_stock)
        incoming_stock: Stock already ordered and in transit (incoming_stock)
        mean_daily_demand: Expected daily sales (from forecast)
        demand_std: Std dev of daily sales
        rop: Reorder point
        safety_stock: Safety stock
        supplier_moq: Supplier Minimum Order Quantity
        supplier_capacity: Supplier Maximum capacity per order
        lead_time_mean: Supplier average lead time (days)
        lead_time_std: Supplier lead time standard deviation
        service_level: Configured service level (0.90, 0.95, 0.99)
        unit_cost: Cost per unit of the item

    Returns:
        dict: A recommendation dict matching PORecommendation schema
    """
    # Net available stock = physical + incoming - allocated
    available = current_stock + incoming_stock - allocated_stock
    lead_time_demand = mean_daily_demand * lead_time_mean

    # Target inventory level: ROP + lead_time_demand (safety stock replenishment size)
    target_inventory = rop + lead_time_demand

    should_order = available < rop

    if should_order:
        # Calculate raw replenishment need
        raw_qty = max(0.0, target_inventory - available)
        
        # Round up to supplier MOQ
        if raw_qty > 0:
            moq = max(1, supplier_moq)
            recommended_qty = int(np.ceil(raw_qty / moq) * moq)
        else:
            recommended_qty = 0

        # Cap at supplier capacity
        if recommended_qty > supplier_capacity:
            recommended_qty = supplier_capacity
            cap_reason = f" (Capped at supplier capacity limit of {supplier_capacity})"
        else:
            cap_reason = ""

        # Urgency: CRITICAL if available stock is less than 50% of safety stock, else HIGH
        if available < (safety_stock * 0.5):
            urgency = "CRITICAL"
        else:
            urgency = "HIGH"

        # Calculate stockout risk using Monte Carlo simulation
        risk_res = calculate_stockout_probability(
            initial_inventory=available,
            mean_daily_demand=mean_daily_demand,
            demand_std=demand_std,
            mean_lead_time=lead_time_mean,
            lead_time_std=lead_time_std,
            num_simulations=500
        )
        stockout_prob = risk_res["stockout_probability"]

        # Calculate projected stockout date
        proj_date = calculate_stockout_date(
            available_stock=available,
            mean_daily_demand=mean_daily_demand,
            from_date=date.today()
        )

        reason = (
            f"Net available stock ({available:.1f}) fell below dynamic Reorder Point ({rop:.1f}). "
            f"Replenishing to meet lead time demand ({lead_time_demand:.1f}) and safety stock ({safety_stock:.1f})."
            f"{cap_reason}"
        )

        estimated_cost = recommended_qty * unit_cost if unit_cost is not None else None

        import uuid
        recommendation_id = f"rec-{uuid.uuid4().hex[:8]}"

        return {
            "should_order": True,
            "recommendation_id": recommendation_id,
            "sku_id": sku_id,
            "sku_name": sku_name,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "recommended_qty": recommended_qty,
            "current_stock": current_stock,
            "available_stock": available,
            "incoming_stock": incoming_stock,
            "rop": round(rop, 2),
            "safety_stock": round(safety_stock, 2),
            "lead_time_demand": round(lead_time_demand, 2),
            "target_inventory": round(target_inventory, 2),
            "supplier_moq": supplier_moq,
            "stockout_probability": stockout_prob,
            "projected_stockout_date": proj_date,
            "urgency": urgency,
            "reason": reason,
            "estimated_cost": estimated_cost
        }
    else:
        return {
            "should_order": False,
            "recommendation_id": "",
            "sku_id": sku_id,
            "sku_name": sku_name,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "recommended_qty": 0,
            "current_stock": current_stock,
            "available_stock": available,
            "incoming_stock": incoming_stock,
            "rop": round(rop, 2),
            "safety_stock": round(safety_stock, 2),
            "lead_time_demand": round(lead_time_demand, 2),
            "target_inventory": round(target_inventory, 2),
            "supplier_moq": supplier_moq,
            "stockout_probability": 0.0,
            "projected_stockout_date": None,
            "urgency": "LOW",
            "reason": f"Net available stock ({available:.1f}) is healthy (above ROP: {rop:.1f}). No purchase order recommended.",
            "estimated_cost": 0.0
        }
