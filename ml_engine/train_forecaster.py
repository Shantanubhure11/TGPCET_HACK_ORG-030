"""
LightGBM Quantile Regression Training Pipeline.
Trains 3 models (P10, P50, P90) per SKU group.
"""
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import lightgbm as lgb
import numpy as np
import pandas as pd

from ml_engine.data_loader import load_sales_from_db, load_sales_from_csv, create_full_date_grid
from ml_engine.feature_engineering import engineer_features, prepare_train_val_split, get_feature_columns
from ml_engine.evaluate import calculate_wape, calculate_rmse, calculate_pinball_loss
from ml_engine.model_registry import save_models, ModelBundle

logger = logging.getLogger(__name__)

# LightGBM base params — same for all quantiles
LGB_BASE_PARAMS = {
    "objective": "quantile",
    "metric": "quantile",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": -1,
    "seed": 42,
    "n_jobs": -1,
}

QUANTILES = [0.1, 0.5, 0.9]    # P10, P50, P90
QUANTILE_NAMES = {0.1: "p10", 0.5: "p50", 0.9: "p90"}


def train_forecaster(
    df: pd.DataFrame,
    num_boost_round: int = 1000,
    early_stopping_rounds: int = 50,
    train_ratio: float = 0.8,
) -> Tuple[Dict, dict, Dict]:
    """
    Train LightGBM quantile models on the provided sales DataFrame.

    Returns:
        models       — {quantile: lgb.Booster}
        sku_encoder  — {sku_id: int}
        metrics      — {wape, rmse, pinball_p10, pinball_p90}
    """
    logger.info(f"Starting model training on {len(df)} rows, {df['sku_id'].nunique()} SKUs")
    t0 = time.time()

    # Feature engineering
    df_feat, sku_encoder = engineer_features(df)

    # Train/val split
    X_train, y_train, X_val, y_val, cutoff_date, feature_cols = prepare_train_val_split(
        df_feat, train_ratio=train_ratio
    )
    logger.info(
        f"Train: {len(X_train)} rows (up to {cutoff_date}), "
        f"Val: {len(X_val)} rows"
    )

    train_ds = lgb.Dataset(X_train, label=y_train, feature_name=feature_cols)
    val_ds = lgb.Dataset(X_val, label=y_val, reference=train_ds, feature_name=feature_cols)

    models = {}
    val_predictions = {}

    for q in QUANTILES:
        params = {**LGB_BASE_PARAMS, "alpha": q}
        logger.info(f"Training quantile q={q} ({QUANTILE_NAMES[q].upper()})...")

        callbacks = [lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=False),
                     lgb.log_evaluation(period=-1)]

        model = lgb.train(
            params,
            train_ds,
            num_boost_round=num_boost_round,
            valid_sets=[val_ds],
            callbacks=callbacks,
        )
        models[q] = model
        val_predictions[QUANTILE_NAMES[q]] = model.predict(X_val)
        logger.info(f"  → Best iteration: {model.best_iteration}")

    # Evaluate on validation set
    metrics = _evaluate_models(y_val, val_predictions)
    elapsed = time.time() - t0
    logger.info(
        f"Training complete in {elapsed:.1f}s | "
        f"WAPE: {metrics['wape']:.3f} | RMSE: {metrics['rmse']:.2f}"
    )

    return models, sku_encoder, metrics, feature_cols


def _evaluate_models(y_true: np.ndarray, predictions: dict) -> dict:
    """Compute evaluation metrics on validation set."""
    p50 = predictions.get("p50", predictions.get(0.5, np.zeros_like(y_true)))
    p10 = predictions.get("p10", predictions.get(0.1, np.zeros_like(y_true)))
    p90 = predictions.get("p90", predictions.get(0.9, np.zeros_like(y_true)))

    return {
        "wape": calculate_wape(y_true, p50),
        "rmse": calculate_rmse(y_true, p50),
        "pinball_p10": calculate_pinball_loss(y_true, p10, 0.1),
        "pinball_p90": calculate_pinball_loss(y_true, p90, 0.9),
    }


def train_and_save(
    db_session=None,
    csv_path: Optional[str] = None,
    model_dir: str = "./models",
    sku_ids: Optional[List[str]] = None,
    lookback_days: int = 365,
    num_boost_round: int = 1000,
    early_stopping_rounds: int = 50,
) -> dict:
    """
    Full pipeline: load data → engineer features → train → save models.
    Called by scripts/train_models.py or the FastAPI retrain endpoint.
    """
    os.makedirs(model_dir, exist_ok=True)

    # Load data
    if db_session is not None:
        df_raw = load_sales_from_db(db_session, sku_ids=sku_ids, days_back=lookback_days)
    elif csv_path:
        df_raw = load_sales_from_csv(csv_path)
    else:
        raise ValueError("Must provide either db_session or csv_path")

    if df_raw.empty:
        logger.error("No sales data available for training")
        return {"status": "failed", "reason": "no_data"}

    # Fill date grid
    df_full = create_full_date_grid(df_raw)

    # Train
    models, sku_encoder, metrics, feature_cols = train_forecaster(
        df_full,
        num_boost_round=num_boost_round,
        early_stopping_rounds=early_stopping_rounds,
    )

    # Save
    bundle = ModelBundle(
        models=models,
        sku_encoder=sku_encoder,
        feature_cols=feature_cols,
        metrics=metrics,
        trained_at=datetime.utcnow(),
    )
    save_path = save_models(bundle, model_dir)
    logger.info(f"Models saved to {save_path}")

    return {
        "status": "success",
        "model_path": save_path,
        "metrics": metrics,
        "num_skus": df_full["sku_id"].nunique(),
        "training_rows": len(df_full),
    }
