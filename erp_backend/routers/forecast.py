"""
Forecast API Router.
Endpoints for demand prediction retrieval and ML retraining.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from erp_backend.database import get_db
from erp_backend.schemas.forecast import ForecastRead, RetrainRequest
from erp_backend.services.demand_forecasting_service import get_forecast_for_sku, run_model_retraining

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forecast", tags=["Demand Forecasting"])

@router.get("/demand", response_model=ForecastRead)
def get_demand_forecast(
    sku_id: str = Query(..., description="SKU ID to query forecast"),
    horizon: int = Query(30, ge=7, le=90, description="Forecast horizon in days"),
    db: Session = Depends(get_db)
):
    """
    Get P10, P50, and P90 quantile demand forecast for a specified SKU.
    Loads from cache if available, or dynamically generates from the model.
    """
    try:
        forecast = get_forecast_for_sku(db, sku_id, horizon)
        return forecast
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error querying forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error generating forecast")

@router.post("/retrain")
def retrain_forecaster_models(
    payload: RetrainRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger retraining of the LightGBM Quantile models based on latest database transaction logs.
    """
    result = run_model_retraining(
        db=db,
        sku_ids=payload.sku_ids,
        lookback_days=payload.lookback_days
    )
    if result.get("status") == "success":
        return {"status": "success", "message": "Model retrained successfully", "metrics": result.get("metrics")}
    else:
        raise HTTPException(status_code=500, detail=f"Model training failed: {result.get('reason')}")
