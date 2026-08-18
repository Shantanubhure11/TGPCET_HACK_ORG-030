"""Pydantic schemas for Demand Forecasts."""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    forecast_date: date
    p10: Optional[float]
    p50: Optional[float]
    p90: Optional[float]
    actual: Optional[float] = None      # Historical actual (for comparison charts)


class ModelMetrics(BaseModel):
    wape: Optional[float] = None
    rmse: Optional[float] = None
    pinball_loss_p10: Optional[float] = None
    pinball_loss_p90: Optional[float] = None


class ForecastRead(BaseModel):
    sku_id: str
    sku_name: Optional[str] = None
    run_date: date
    horizon: int
    forecast: List[ForecastPoint]
    model_metrics: ModelMetrics
    model_version: Optional[str] = None


class ForecastRequest(BaseModel):
    sku_id: str
    horizon: int = 30
    days_back: int = 365


class RetrainRequest(BaseModel):
    sku_ids: Optional[List[str]] = None    # None = retrain all SKUs
    lookback_days: int = 365
