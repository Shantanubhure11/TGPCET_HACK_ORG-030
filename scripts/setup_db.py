"""
Database Setup Script.
Initializes the database schema by creating all required tables.
"""
import logging
import sys
import os

# Insert workspace root to system path to resolve imports correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from erp_backend.database import create_all_tables, engine
from erp_backend.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    settings = get_settings()
    logger.info(f"Using database target: {settings.database_url}")
    
    try:
        create_all_tables()
        logger.info("Database schema setup complete! Tables created successfully.")
    except Exception as e:
        logger.critical(f"Failed to setup database: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
