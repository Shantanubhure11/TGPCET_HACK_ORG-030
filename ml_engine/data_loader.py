"""
Data Loader — loads and cleans sales history for ML training.
Supports both DB query and CSV fallback.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def load_sales_from_db(
    db_session,
    sku_ids: Optional[List[str]] = None,
    days_back: int = 365,
) -> pd.DataFrame:
    """
    Load sales history from the database.
    Returns DataFrame with columns:
    [date, sku_id, quantity, price, discount_pct, promotion_flag, stock_available, warehouse_id]
    """
    from erp_backend.models.sales_order import SalesOrder
    from erp_backend.models.item import Item
    from sqlalchemy import func

    cutoff = datetime.utcnow() - timedelta(days=days_back)

    query = db_session.query(
        func.date(SalesOrder.order_date).label("date"),
        SalesOrder.sku_id,
        SalesOrder.warehouse_id,
        func.sum(SalesOrder.order_qty).label("quantity"),
        func.avg(SalesOrder.unit_price).label("price"),
        func.avg(SalesOrder.discount_pct).label("discount_pct"),
        func.max(SalesOrder.promotion_flag.cast(int)).label("promotion_flag"),
        func.avg(SalesOrder.stock_available_at_sale).label("stock_available"),
    ).filter(
        SalesOrder.order_date >= cutoff
    )

    if sku_ids:
        query = query.filter(SalesOrder.sku_id.in_(sku_ids))

    query = query.group_by(
        func.date(SalesOrder.order_date),
        SalesOrder.sku_id,
        SalesOrder.warehouse_id,
    ).order_by("date", SalesOrder.sku_id)

    rows = query.all()
    if not rows:
        logger.warning("No sales data found in DB. Returning empty DataFrame.")
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=[
        "date", "sku_id", "warehouse_id", "quantity",
        "price", "discount_pct", "promotion_flag", "stock_available"
    ])
    df["date"] = pd.to_datetime(df["date"])
    df = _clean_sales_data(df)
    logger.info(f"Loaded {len(df)} sales records for {df['sku_id'].nunique()} SKUs from DB")
    return df


def load_sales_from_csv(csv_path: str) -> pd.DataFrame:
    """
    Load sales history from a CSV file.
    Expected columns: date, sku_id, quantity, price, discount_pct, promotion_flag, stock_available
    """
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = _clean_sales_data(df)
    logger.info(f"Loaded {len(df)} rows from {csv_path}")
    return df


def _clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean sales data."""
    if df.empty:
        return df

    # Enforce data types
    df["date"] = pd.to_datetime(df["date"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).clip(lower=0)

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).clip(lower=0)
    else:
        df["price"] = 0.0

    if "discount_pct" in df.columns:
        df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").fillna(0).clip(0, 100)
    else:
        df["discount_pct"] = 0.0

    if "promotion_flag" in df.columns:
        df["promotion_flag"] = df["promotion_flag"].fillna(0).astype(int)
    else:
        df["promotion_flag"] = 0

    if "stock_available" in df.columns:
        df["stock_available"] = pd.to_numeric(df["stock_available"], errors="coerce").fillna(0).clip(lower=0)
    else:
        df["stock_available"] = 0.0

    # Remove duplicates
    if "warehouse_id" in df.columns:
        df = df.drop_duplicates(subset=["date", "sku_id", "warehouse_id"])
    else:
        df = df.drop_duplicates(subset=["date", "sku_id"])

    df = df.sort_values("date").reset_index(drop=True)
    return df


def create_full_date_grid(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a complete date grid for each SKU (fill gaps with 0 demand).
    This ensures continuity for lag/rolling features.
    """
    if df.empty:
        return df

    date_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    sku_ids = df["sku_id"].unique()

    grid = pd.MultiIndex.from_product(
        [date_range, sku_ids], names=["date", "sku_id"]
    ).to_frame(index=False)

    # Keep the primary warehouse per SKU
    if "warehouse_id" in df.columns:
        primary_wh = df.groupby("sku_id")["warehouse_id"].agg(lambda x: x.mode()[0]).reset_index()
        grid = grid.merge(primary_wh, on="sku_id", how="left")

    df_full = grid.merge(df, on=["date", "sku_id"], how="left", suffixes=("", "_drop"))
    df_full = df_full[[c for c in df_full.columns if not c.endswith("_drop")]]

    # Fill numeric columns with 0 for missing days
    numeric_cols = ["quantity", "price", "discount_pct", "promotion_flag", "stock_available"]
    for col in numeric_cols:
        if col in df_full.columns:
            df_full[col] = df_full[col].fillna(0)

    # Forward-fill price (price doesn't change to 0 on non-sale days)
    if "price" in df_full.columns:
        df_full["price"] = df_full.groupby("sku_id")["price"].transform(
            lambda x: x.replace(0, np.nan).ffill().bfill().fillna(0)
        )

    return df_full.sort_values(["sku_id", "date"]).reset_index(drop=True)
