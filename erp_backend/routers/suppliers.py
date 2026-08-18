"""
Suppliers API Router.
Handles supplier information retrieval and performance metrics.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from erp_backend.database import get_db
from erp_backend.schemas.supplier import SupplierRead, SupplierPerformance
from erp_backend.models.supplier import Supplier
from erp_backend.models.purchase_order import PurchaseOrder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/suppliers", tags=["Supplier Management"])

@router.get("", response_model=List[SupplierRead])
def list_suppliers(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns list of all suppliers configured in the ERP database.
    """
    suppliers = db.query(Supplier).offset(offset).limit(limit).all()
    return suppliers

@router.get("/{supplier_id}/performance", response_model=SupplierPerformance)
def get_supplier_performance(
    supplier_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns lead time averages, delivery reliability, MOQ, capacity,
    and active order metrics for a supplier.
    """
    sup = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")

    # Count purchase orders
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier_id).all()
    total_orders = len(pos)
    pending_orders = len([p for p in pos if p.status in ["PENDING", "CONFIRMED", "SHIPPED"]])

    return {
        "supplier_id": sup.supplier_id,
        "name": sup.name,
        "on_time_delivery_pct": float(sup.reliability_pct),
        "avg_lead_time_days": float(sup.avg_lead_time),
        "lead_time_std": float(sup.lead_time_std),
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "moq": sup.moq
    }
