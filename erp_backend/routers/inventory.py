"""
Inventory API Router.
Handles inventory health inquiries, ledger audit logs, and stock adjustments.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from erp_backend.database import get_db
from erp_backend.schemas.inventory import InventoryRead, InventoryAdjust, LedgerEntryRead
from erp_backend.models.inventory import Inventory
from erp_backend.models.inventory_ledger import InventoryLedger
from erp_backend.models.item import Item
from erp_backend.services.inventory_service import get_inventory_status_by_sku, adjust_inventory_stock

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

@router.get("/current", response_model=InventoryRead)
def get_current_inventory_status(
    sku_id: str = Query(..., description="SKU ID to check"),
    warehouse_id: str = Query("WH-01", description="Warehouse ID to query"),
    db: Session = Depends(get_db)
):
    """
    Returns inventory balance, dynamic safety stock, ROP, days of inventory,
    and Monte Carlo replenishment stockout risk.
    """
    # Check if SKU exists
    item = db.query(Item).filter(Item.sku_id == sku_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"SKU {sku_id} not found in master data")

    status = get_inventory_status_by_sku(db, sku_id, warehouse_id)
    if not status:
        # If no inventory record exists, try to auto-initialize it to 0
        adjust_inventory_stock(db, InventoryAdjust(
            sku_id=sku_id,
            warehouse_id=warehouse_id,
            qty_change=0,
            reason="INITIAL",
            notes="Auto-initialized"
        ))
        status = get_inventory_status_by_sku(db, sku_id, warehouse_id)
        
    return status

@router.get("/list", response_model=List[InventoryRead])
def list_all_inventory_health(
    warehouse_id: str = Query("WH-01", description="Warehouse ID to check"),
    db: Session = Depends(get_db)
):
    """
    Returns complete inventory health list for all SKUs.
    Useful for populating dashboards.
    """
    records = db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id).all()
    results = []
    for r in records:
        try:
            status = get_inventory_status_by_sku(db, r.sku_id, warehouse_id)
            if status:
                results.append(status)
        except Exception as e:
            logger.error(f"Failed to calculate health for SKU {r.sku_id}: {e}")
    return results

@router.get("/ledger", response_model=List[LedgerEntryRead])
def get_inventory_ledger_audit(
    sku_id: Optional[str] = Query(None, description="Filter by SKU ID"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns immutable audit trail history logs of all inventory changes.
    """
    query = db.query(InventoryLedger)
    if sku_id:
        query = query.filter(InventoryLedger.sku_id == sku_id)
        
    ledger_entries = query.order_by(desc(InventoryLedger.timestamp)).offset(offset).limit(limit).all()
    return ledger_entries

@router.post("/adjust")
def adjust_inventory_level(
    payload: InventoryAdjust,
    db: Session = Depends(get_db)
):
    """
    Adjust current physical stock level. Automatically inserts a ledger record.
    """
    # Check if SKU exists
    item = db.query(Item).filter(Item.sku_id == payload.sku_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"SKU {payload.sku_id} not found in master data")

    try:
        res = adjust_inventory_stock(db, payload)
        return res
    except Exception as e:
        logger.error(f"Adjustment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Stock adjustment database transaction failed")
