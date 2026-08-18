"""
Main FastAPI entry point.
Integrates forecast, inventory, supplier, purchase order, simulation, alert, and IoT routers.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from erp_backend.config import get_settings
from erp_backend.database import create_all_tables
from erp_backend.routers import forecast, inventory, suppliers, purchases, simulation, alerts, iot

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager handling database initializations."""
    logger.info("Starting supply chain twin ERP Backend server...")
    
    # Auto-create tables for development convenience (especially SQLite)
    try:
        create_all_tables()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        
    yield
    logger.info("Shutting down ERP Backend server...")

# Initialize FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the AI-Powered Supply Chain Digital Twin.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(forecast.router)
app.include_router(inventory.router)
app.include_router(suppliers.router)
app.include_router(purchases.router)
app.include_router(simulation.router)
app.include_router(alerts.router)
app.include_router(iot.router)

@app.get("/health")
def health_check():
    """Simple API status checks."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database": "sqlite/postgresql"
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Supply Chain Digital Twin ERP API. Go to /docs for Swagger API specifications."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.api_port, reload=True)
