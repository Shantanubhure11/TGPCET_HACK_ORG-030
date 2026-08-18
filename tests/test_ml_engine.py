"""
Unit tests for the ML Forecasting Pipeline (feature engineering, evaluations).
"""
import pandas as pd
import numpy as np
import pytest
from ml_engine.feature_engineering import engineer_features, prepare_train_val_split
from ml_engine.evaluate import calculate_wape, calculate_rmse, calculate_pinball_loss

def test_feature_engineering():
    """Verify that lag and rolling features are correctly generated."""
    # Create simple historical df
    dates = pd.date_range(start="2026-01-01", periods=40)
    df = pd.DataFrame({
        "date": dates,
        "sku_id": ["SKU-1"] * 40,
        "quantity": [10.0] * 40,
        "price": [100.0] * 40,
        "discount_pct": [0.0] * 40,
        "promotion_flag": [0] * 40,
        "stock_available": [50.0] * 40
    })
    
    engineered, encoder = engineer_features(df)
    
    assert "lag_1" in engineered.columns
    assert "rolling_mean_7" in engineered.columns
    assert "day_of_week" in engineered.columns
    # Check that lag_1 matches the previous day's quantity (after row 0)
    assert engineered.loc[1, "lag_1"] == 10.0

def test_evaluation_metrics():
    """Verify WAPE, RMSE, and Pinball loss math formulas."""
    y_true = np.array([10.0, 20.0, 15.0])
    y_pred = np.array([12.0, 18.0, 15.0])
    
    wape = calculate_wape(y_true, y_pred)
    # Sum of abs diff: 2 + 2 + 0 = 4. Sum true: 45. WAPE = 4 / 45 = 0.0888
    assert wape == pytest.approx(0.0888, abs=0.001)

    rmse = calculate_rmse(y_true, y_pred)
    # Mean sq diff: (4 + 4 + 0) / 3 = 2.666. RMSE = sqrt(2.666) = 1.633
    assert rmse == pytest.approx(1.633, abs=0.001)

    pinball = calculate_pinball_loss(y_true, y_pred, 0.5)
    # errors = [-2, 2, 0]
    # loss: errors >=0 -> q * errors. errors <0 -> (q-1)*errors
    # 1st error -2: loss = (0.5 - 1) * -2 = 1
    # 2nd error 2: loss = 0.5 * 2 = 1
    # 3rd error 0: loss = 0
    # Mean loss = (1+1+0)/3 = 0.666
    assert pinball == pytest.approx(0.666, abs=0.001)
