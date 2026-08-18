"""
Model Registry — serialize and load LightGBM models with metadata.
"""
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

import joblib
import lightgbm as lgb

logger = logging.getLogger(__name__)

MODEL_FILENAME = "lightgbm_quantile_models.joblib"
METADATA_FILENAME = "model_metadata.json"


@dataclass
class ModelBundle:
    """Container for trained models + metadata."""
    models: Dict                      # {quantile: lgb.Booster}
    sku_encoder: Dict[str, int]
    feature_cols: List[str]
    metrics: Dict
    trained_at: datetime
    version: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y%m%d_%H%M%S"))


def save_models(bundle: ModelBundle, model_dir: str = "./models") -> str:
    """Serialize model bundle to disk."""
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, MODEL_FILENAME)
    meta_path = os.path.join(model_dir, METADATA_FILENAME)

    # Save models with joblib
    joblib.dump(bundle, model_path)

    # Save human-readable metadata
    meta = {
        "version": bundle.version,
        "trained_at": bundle.trained_at.isoformat(),
        "num_skus": len(bundle.sku_encoder),
        "feature_cols": bundle.feature_cols,
        "metrics": bundle.metrics,
        "quantiles": [0.1, 0.5, 0.9],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Model saved → {model_path}")
    return model_path


def load_models(model_dir: str = "./models") -> Optional[ModelBundle]:
    """Load model bundle from disk. Returns None if not found."""
    model_path = os.path.join(model_dir, MODEL_FILENAME)
    if not os.path.exists(model_path):
        logger.warning(f"No model found at {model_path}")
        return None
    bundle = joblib.load(model_path)
    logger.info(f"Model loaded from {model_path} (v{bundle.version})")
    return bundle


def load_metadata(model_dir: str = "./models") -> Optional[dict]:
    """Load model metadata JSON."""
    meta_path = os.path.join(model_dir, METADATA_FILENAME)
    if not os.path.exists(meta_path):
        return None
    with open(meta_path) as f:
        return json.load(f)


def model_exists(model_dir: str = "./models") -> bool:
    return os.path.exists(os.path.join(model_dir, MODEL_FILENAME))
