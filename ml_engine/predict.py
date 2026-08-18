"""
Demand Prediction — generate P10/P50/P90 forecasts using trained models.
"""
import logging
from datetime import date, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd

from ml_engine.model_registry import load_models, model_exists
from ml_engine.feature_engineering import build_future_features, get_feature_columns
from ml_engine.data_loader import load_sales_from_db, create_full_date_grid

logger = logging.getLogger(__name__)


def predict_demand(
    sku_id: str,
    horizon_days: int = 30,
    model_dir: str = "./models",
    db_session=None,
    lookback_days: int = 365,
) -> Optional[pd.DataFrame]:
    """
    Generate demand forecast for a single SKU.

    Returns DataFrame with columns:
    [forecast_date, p10, p50, p90]
    """
    if not model_exists(model_dir):
        logger.error("No trained model found. Run train_models.py first.")
        return None

    bundle = load_models(model_dir)
    if bundle is None:
        return None

    # Load recent history for lag/rolling features
    if db_session is not None:
        df_hist = load_sales_from_db(db_session, sku_ids=[sku_id], days_back=lookback_days)
        df_hist = create_full_date_grid(df_hist)
    else:
        # Fallback: minimal synthetic history
        df_hist = _make_synthetic_history(sku_id, lookback_days)

    # Build feature rows for future dates
    future_features = build_future_features(
        df_hist, sku_id, horizon_days, bundle.sku_encoder
    )

    if future_features.empty:
        logger.warning(f"No future features generated for SKU {sku_id}")
        return None

    feature_cols = [c for c in bundle.feature_cols if c in future_features.columns]
    X_future = future_features[feature_cols].values

    # Predict
    predictions = {q: bundle.models[q].predict(X_future) for q in [0.1, 0.5, 0.9]}

    # Clip negatives
    for q in predictions:
        predictions[q] = np.clip(predictions[q], 0, None)

    # Enforce P10 <= P50 <= P90
    p10 = predictions[0.1]
    p50 = predictions[0.5]
    p90 = predictions[0.9]
    p10 = np.minimum(p10, p50)
    p90 = np.maximum(p90, p50)

    result = pd.DataFrame({
        "forecast_date": future_features["date"].values,
        "p10": p10,
        "p50": p50,
        "p90": p90,
    })

    logger.info(f"Forecast generated for SKU {sku_id}: {len(result)} days, mean P50={p50.mean():.1f}")
    return result


def predict_all_skus(
    sku_ids: List[str],
    horizon_days: int = 30,
    model_dir: str = "./models",
    db_session=None,
) -> dict:
    """Generate forecasts for multiple SKUs. Returns {sku_id: DataFrame}."""
    results = {}
    for sku_id in sku_ids:
        try:
            df = predict_demand(sku_id, horizon_days, model_dir, db_session)
            if df is not None:
                results[sku_id] = df
        except Exception as e:
            logger.error(f"Forecast failed for {sku_id}: {e}")
    return results


def get_demand_stats(forecast_df: pd.DataFrame) -> dict:
    """Aggregate forecast stats for inventory calculations."""
    if forecast_df is None or forecast_df.empty:
        return {"mean_daily_p50": 0, "std_daily": 0, "total_p50": 0}
    return {
        "mean_daily_p50": float(forecast_df["p50"].mean()),
        "mean_daily_p10": float(forecast_df["p10"].mean()),
        "mean_daily_p90": float(forecast_df["p90"].mean()),
        "std_daily": float(forecast_df["p50"].std()),
        "total_p50": float(forecast_df["p50"].sum()),
        "total_p10": float(forecast_df["p10"].sum()),
        "total_p90": float(forecast_df["p90"].sum()),
    }


def _make_synthetic_history(sku_id: str, days: int) -> pd.DataFrame:
    """Minimal synthetic history for when DB is unavailable."""
    np.random.seed(hash(sku_id) % (2 ** 32))
    dates = pd.date_range(end=date.today(), periods=days)
    qty = np.random.gamma(shape=5, scale=10, size=days)
    return pd.DataFrame({
        "date": dates, "sku_id": sku_id, "quantity": qty,
        "price": 50.0, "discount_pct": 0.0,
        "promotion_flag": 0, "stock_available": 100.0
    })
