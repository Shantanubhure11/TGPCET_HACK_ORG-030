"""
Model evaluation metrics: WAPE, RMSE, Pinball Loss.
"""
import numpy as np


def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Weighted Absolute Percentage Error.
    WAPE = Σ|y - ŷ| / Σy × 100%
    Lower is better. Target: < 20%.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    total_demand = np.sum(y_true)
    if total_demand == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_demand)


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_pinball_loss(
    y_true: np.ndarray, y_pred: np.ndarray, quantile: float
) -> float:
    """
    Pinball (Quantile) Loss.
    Measures calibration quality of a quantile forecast.
    Lower is better.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    errors = y_true - y_pred
    loss = np.where(errors >= 0, quantile * errors, (quantile - 1) * errors)
    return float(np.mean(loss))


def evaluate_by_sku(
    df_val,       # DataFrame with [sku_id, quantity, p10_pred, p50_pred, p90_pred]
) -> dict:
    """Per-SKU evaluation report."""
    results = {}
    for sku_id, grp in df_val.groupby("sku_id"):
        y = grp["quantity"].values
        results[sku_id] = {
            "wape": calculate_wape(y, grp["p50_pred"].values),
            "rmse": calculate_rmse(y, grp["p50_pred"].values),
            "pinball_p10": calculate_pinball_loss(y, grp["p10_pred"].values, 0.1),
            "pinball_p90": calculate_pinball_loss(y, grp["p90_pred"].values, 0.9),
            "n_rows": len(grp),
        }
    return results


def forecast_quality_label(wape: float) -> str:
    """Human-readable forecast quality label."""
    if wape < 0.10:
        return "EXCELLENT"
    elif wape < 0.20:
        return "GOOD"
    elif wape < 0.30:
        return "FAIR"
    else:
        return "POOR"
