"""
Feature Engineering for LightGBM demand forecasting.
Generates temporal, lag, rolling, commercial, and inventory features.
"""
import logging
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Indian public holidays (simplified set — extend as needed)
INDIAN_HOLIDAYS = {
    "01-26",  # Republic Day
    "08-15",  # Independence Day
    "10-02",  # Gandhi Jayanti
    "12-25",  # Christmas
    "11-01",  # Diwali (approximate)
    "03-25",  # Holi (approximate)
}

FEATURE_COLUMNS = [
    # Temporal
    "day_of_week", "day_of_month", "month", "quarter",
    "week_of_year", "is_weekend", "is_month_start", "is_month_end",
    "is_quarter_start", "is_holiday",
    # Lag features
    "lag_1", "lag_7", "lag_14", "lag_30",
    # Rolling aggregates
    "rolling_mean_7", "rolling_std_7",
    "rolling_mean_14", "rolling_std_14",
    "rolling_mean_30", "rolling_std_30",
    # Commercial
    "price", "discount_pct", "promotion_flag",
    # Inventory
    "stock_available", "is_zero_demand", "is_stockout",
    # SKU encoding
    "sku_encoded",
]

TARGET_COLUMN = "quantity"


def engineer_features(df: pd.DataFrame, sku_encoder: dict = None) -> pd.DataFrame:
    """
    Full feature engineering pipeline.

    Input: DataFrame with [date, sku_id, quantity, price, discount_pct,
                           promotion_flag, stock_available]
    Output: DataFrame with all FEATURE_COLUMNS + target column
    """
    if df.empty:
        return df

    df = df.copy()
    df = df.sort_values(["sku_id", "date"]).reset_index(drop=True)

    # --- Temporal Features ---
    df["day_of_week"] = df["date"].dt.dayofweek         # 0=Mon, 6=Sun
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
    df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
    df["is_quarter_start"] = df["date"].dt.is_quarter_start.astype(int)
    df["is_holiday"] = df["date"].apply(
        lambda d: int(f"{d.month:02d}-{d.day:02d}" in INDIAN_HOLIDAYS)
    )

    # --- Lag Features (per SKU) ---
    for lag in [1, 7, 14, 30]:
        df[f"lag_{lag}"] = df.groupby("sku_id")["quantity"].shift(lag)

    # --- Rolling Aggregates (per SKU) ---
    for window in [7, 14, 30]:
        rolled = df.groupby("sku_id")["quantity"].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1)
        )
        df[f"rolling_mean_{window}"] = rolled.mean()
        df[f"rolling_std_{window}"] = rolled.std().fillna(0)

    # --- Commercial Features ---
    if "discount_pct" not in df.columns:
        df["discount_pct"] = 0.0
    if "promotion_flag" not in df.columns:
        df["promotion_flag"] = 0
    if "price" not in df.columns:
        df["price"] = 0.0
    if "stock_available" not in df.columns:
        df["stock_available"] = 0.0

    df["discount_pct"] = df["discount_pct"].clip(0, 100)

    # --- Inventory Features ---
    df["is_zero_demand"] = (df["quantity"] == 0).astype(int)
    df["is_stockout"] = (
        (df["quantity"] > 0) & (df["stock_available"] == 0)
    ).astype(int)

    # --- SKU Encoding ---
    if sku_encoder is None:
        sku_list = sorted(df["sku_id"].unique())
        sku_encoder = {sku: idx for idx, sku in enumerate(sku_list)}
    df["sku_encoded"] = df["sku_id"].map(sku_encoder).fillna(-1).astype(int)

    # Fill lag NaN at start of series with 0
    lag_cols = [c for c in df.columns if c.startswith("lag_") or c.startswith("rolling_")]
    df[lag_cols] = df[lag_cols].fillna(0)

    logger.info(
        f"Feature engineering complete: {len(df)} rows, "
        f"{df['sku_id'].nunique()} SKUs, {len(FEATURE_COLUMNS)} features"
    )
    return df, sku_encoder


def get_feature_columns(df: pd.DataFrame) -> List[str]:
    """Return available feature columns from engineered DataFrame."""
    return [c for c in FEATURE_COLUMNS if c in df.columns]


def prepare_train_val_split(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple:
    """
    Time-based train/validation split (respects temporal ordering).
    Returns (X_train, y_train, X_val, y_val, cutoff_date)
    """
    df = df.sort_values("date")
    cutoff_idx = int(len(df) * train_ratio)
    cutoff_date = df.iloc[cutoff_idx]["date"]

    train = df[df["date"] < cutoff_date]
    val = df[df["date"] >= cutoff_date]

    feature_cols = get_feature_columns(df)

    X_train = train[feature_cols].values
    y_train = train[TARGET_COLUMN].values
    X_val = val[feature_cols].values
    y_val = val[TARGET_COLUMN].values

    return X_train, y_train, X_val, y_val, cutoff_date, feature_cols


def build_future_features(
    historical_df: pd.DataFrame,
    sku_id: str,
    horizon_days: int,
    sku_encoder: dict,
) -> pd.DataFrame:
    """
    Build feature rows for future dates (no actuals known).
    Uses last known price, averages for commercial features.
    Lag/rolling features are extrapolated from recent history.
    """
    sku_df = historical_df[historical_df["sku_id"] == sku_id].sort_values("date")
    if sku_df.empty:
        return pd.DataFrame()

    last_date = sku_df["date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon_days)

    # Build rows
    rows = []
    for fd in future_dates:
        rows.append({
            "date": fd,
            "sku_id": sku_id,
            "quantity": np.nan,     # Unknown
            "price": sku_df["price"].iloc[-1] if "price" in sku_df.columns else 0,
            "discount_pct": 0.0,
            "promotion_flag": 0,
            "stock_available": 0.0,
        })

    future_df = pd.DataFrame(rows)

    # Append to history and re-engineer to get lag/rolling right
    combined = pd.concat([sku_df, future_df], ignore_index=True)
    combined_feat, _ = engineer_features(combined, sku_encoder)

    # Return only the future rows
    return combined_feat[combined_feat["date"].isin(future_dates)].reset_index(drop=True)
