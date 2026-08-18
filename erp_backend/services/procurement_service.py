"""
Procurement Service.
Handles PO creation, PO recommendations, and Goods Receipt Notes (GRN).
"""
import logging
from datetime import date, datetime
from sqlalchemy.orm import Session
from erp_backend.models.purchase_order import PurchaseOrder
from erp_backend.models.goods_receipt import GoodsReceiptNote
from erp_backend.models.item import Item
from erp_backend.models.supplier import Supplier
from erp_backend.models.inventory import Inventory
from erp_backend.schemas.purchase_order import POCreate, GRNCreate
from erp_backend.services.inventory_service import get_inventory_status_by_sku, adjust_inventory_stock
from erp_backend.schemas.inventory import InventoryAdjust
from inventory_engine.procurement import recommend_purchase_order

logger = logging.getLogger(__name__)

def generate_procurement_recommendations(db: Session, service_level: float = 0.95) -> list:
    """
    Evaluates all items in inventory and returns pending purchase order recommendations.
    """
    items = db.query(Item).all()
    recommendations = []

    for item in items:
        # Get supplier details
        supplier = db.query(Supplier).filter(Supplier.supplier_id == item.supplier_id).first()
        if not supplier:
            continue

        # Get inventory health status
        # For simplicity, aggregate across warehouses or use primary WH-01
        inv_health = get_inventory_status_by_sku(db, item.sku_id, "WH-01")
        if not inv_health:
            continue

        # Generate forecast stats to supply ROP/SS calculations
        forecast_res = get_forecast_for_sku(db, item.sku_id, horizon=30)
        p50_demands = [p["p50"] for p in forecast_res["forecast"]]
        mean_demand = float(sum(p50_demands) / len(p50_demands)) if p50_demands else 10.0
        demand_std = float(max(1.0, float(np.std(p50_demands)))) if p50_demands else 2.0

        rec = recommend_purchase_order(
            sku_id=item.sku_id,
            sku_name=item.name,
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.name,
            current_stock=inv_health["physical_stock"],
            allocated_stock=inv_health["allocated_stock"],
            incoming_stock=inv_health["incoming_stock"],
            mean_daily_demand=mean_demand,
            demand_std=demand_std,
            rop=inv_health["rop"],
            safety_stock=inv_health["safety_stock"],
            supplier_moq=supplier.moq,
            supplier_capacity=supplier.capacity,
            lead_time_mean=supplier.avg_lead_time,
            lead_time_std=supplier.lead_time_std,
            service_level=service_level,
            unit_cost=float(item.unit_cost) if item.unit_cost else 10.0
        )

        if rec["should_order"]:
            recommendations.append(rec)

    return recommendations

def create_purchase_order(db: Session, po_in: POCreate) -> PurchaseOrder:
    """
    Creates a new Purchase Order in the database and updates incoming stock cache.
    """
    import uuid
    po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    po = PurchaseOrder(
        po_number=po_number,
        supplier_id=po_in.supplier_id,
        sku_id=po_in.sku_id,
        order_qty=po_in.order_qty,
        unit_cost=po_in.unit_cost,
        order_date=date.today(),
        expected_delivery=po_in.expected_delivery,
        status="PENDING",
        notes=po_in.notes,
        created_by=po_in.created_by
    )
    db.add(po)
    db.flush()

    # Update incoming stock level in inventory
    inv = db.query(Inventory).filter(
        Inventory.sku_id == po_in.sku_id,
        Inventory.warehouse_id == "WH-01"  # Default warehouse
    ).first()
    if inv:
        inv.incoming_stock = float(inv.incoming_stock) + float(po_in.order_qty)
        
    db.commit()
    logger.info(f"Created PO {po_number} for SKU {po_in.sku_id} (qty={po_in.order_qty})")
    return po

def receive_goods_against_po(db: Session, grn_in: GRNCreate) -> GoodsReceiptNote:
    """
    Records receipt of PO goods, updates physical stock, and clears incoming PO status.
    """
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == grn_in.po_id).first()
    if not po:
        raise ValueError(f"Purchase Order with ID {grn_in.po_id} not found")

    if po.status == "DELIVERED":
        raise ValueError("This Purchase Order has already been delivered")

    import uuid
    grn_number = f"GRN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    discrepancy = float(grn_in.received_qty) - float(po.order_qty)
    has_discrepancy = abs(discrepancy) > 0.01

    grn = GoodsReceiptNote(
        grn_number=grn_number,
        po_id=grn_in.po_id,
        received_qty=grn_in.received_qty,
        ordered_qty=po.order_qty,
        discrepancy_qty=discrepancy,
        received_date=date.today(),
        has_discrepancy=has_discrepancy,
        notes=grn_in.notes
    )
    db.add(grn)

    # 1. Update PO Status
    po.status = "DELIVERED"
    po.actual_delivery = date.today()

    # 2. Adjust physical inventory and decrement incoming stock
    inv = db.query(Inventory).filter(
        Inventory.sku_id == po.sku_id,
        Inventory.warehouse_id == "WH-01"
    ).first()

    if inv:
        # Subtract order_qty from incoming, add received_qty to physical
        inv.incoming_stock = max(0.0, float(inv.incoming_stock) - float(po.order_qty))
        
    db.commit()

    # Call adjustment service to add received_qty to physical and log ledger
    adjust_inventory_stock(db, InventoryAdjust(
        sku_id=po.sku_id,
        warehouse_id="WH-01",
        qty_change=float(grn_in.received_qty),
        reason="PO_RECEIPT",
        notes=f"Received against PO: {po.po_number}",
        user_id="warehouse_manager"
    ))

    logger.info(f"Successfully processed GRN {grn_number} for PO {po.po_number}")
    return grn

import numpy as np
from erp_backend.services.demand_forecasting_service import get_forecast_for_sku
