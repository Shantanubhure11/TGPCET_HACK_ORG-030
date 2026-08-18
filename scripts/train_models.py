"""
Model Training Script.
Triggers offline training of the LightGBM quantile regression models using sales data from the database.
"""
import sys
import os
import logging

# Insert workspace root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from erp_backend.database import SessionLocal
from erp_backend.config import get_settings
from ml_engine.train_forecaster import train_and_save

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    settings = get_settings()
    logger.info("Initializing offline ML forecasting model training...")
    logger.info(f"Target model save folder: {settings.model_directory}")
    
    db = SessionLocal()
    try:
        res = train_and_save(
            db_session=db,
            model_dir=settings.model_directory,
            lookback_days=settings.lookback_days
        )
        if res.get("status") == "success":
            logger.info("Forecaster models retrained successfully!")
            logger.info(f"Save Path: {res.get('model_path')}")
            logger.info(f"WAPE Achieved: {res['metrics']['wape']:.4f} (Target: <0.20)")
            logger.info(f"RMSE Achieved: {res['metrics']['rmse']:.2f}")
        else:
            logger.error(f"Training failed: {res.get('reason')}")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled error during training script execution: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
