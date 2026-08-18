"""
Purchase Order (PO) Router.
Handles PO recommendations, creation, tracking, and GRN receipts.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from erp_backend.database import get_db
from erp_backend.schemas.purchase_order import PORead, POCreate, PORecommendation, GRNCreate
from erp_backend.models.purchase_order import PurchaseOrder
from erp_backend.services.procurement_service import (
    generate_procurement_recommendations, create_purchase_order, receive_goods_against_po
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/purchases", tags=["Procurement & POs"])

@router.get("/recommendations", response_model=List[PORecommendation])
def get_po_recommendations(
    service_level: float = Query(95.0, ge=80, le=99.9, description="Target service level"),
    db: Session = Depends(get_db)
):
    """
    Evaluates current inventory balances vs dynamic safety stock and ROP,
    and returns suggested purchase orders.
    """
    try:
        recs = generate_procurement_recommendations(db, service_level / 100.0)
        return recs
    except Exception as e:
        logger.error(f"Error generating PO recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error calculating procurement needs")

@router.post("/create", response_model=PORead)
def create_new_purchase_order(
    payload: POCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Purchase Order record and increase the incoming inventory count cache.
    """
    try:
        po = create_purchase_order(db, payload)
        return po
    except Exception as e:
        logger.error(f"Failed to create purchase order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Purchase order creation failed")

@router.get("/pending", response_model=List[PORead])
def get_pending_purchase_orders(
    db: Session = Depends(get_db)
):
    """
    Returns list of all active pending purchase orders (not yet received).
    """
    pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.status.in_(["PENDING", "CONFIRMED", "SHIPPED"])
    ).order_by(desc(PurchaseOrder.order_date)).all()
    return pos

@router.get("/all", response_model=List[PORead])
def list_all_purchase_orders(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns list of all purchase orders.
    """
    pos = db.query(PurchaseOrder).order_by(desc(PurchaseOrder.order_date)).offset(offset).limit(limit).all()
    return pos

@router.post("/receive")
def receive_goods(
    payload: GRNCreate,
    db: Session = Depends(get_db)
):
    """
    Receive items against a Purchase Order. Automatically creates a GRN record,
    decrements incoming stock caches, and increases physical warehouse inventory.
    """
    try:
        grn = receive_goods_against_po(db, payload)
        return {"status": "success", "message": f"Goods received. Created note: {grn.grn_number}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to receive goods: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database transaction failed during receipt processing")
