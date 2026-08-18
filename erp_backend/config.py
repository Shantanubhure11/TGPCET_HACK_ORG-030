"""
Configuration management for the ERP backend.
Loads settings from environment variables and YAML config files.
"""
import os
from functools import lru_cache
from typing import List

import yaml
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "AI-Powered Supply Chain Digital Twin"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = Field(
        default="sqlite:///./supply_chain.db",
        description="Database connection URL"
    )

    # MQTT
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_topic_prefix: str = "sensors/warehouse"

    # ML
    model_directory: str = "./models"
    lookback_days: int = 365
    forecast_horizon: int = 30

    # Simulation
    default_service_level: float = 0.95
    default_num_simulations: int = 100
    default_lead_time_mean: float = 3.0
    default_lead_time_std: float = 0.5

    # Inventory
    alert_threshold_pct: float = 10.0
    overstock_doi_threshold: int = 90

    # API
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:8501,http://localhost:3000"

    # Dashboard
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith("postgresql")


def load_yaml_config(config_path: str = "configs/default.yaml") -> dict:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# Z-factors for service levels
Z_FACTORS = {
    0.90: 1.28,
    0.95: 1.65,
    0.99: 2.33,
    90: 1.28,
    95: 1.65,
    99: 2.33,
}

# Risk classification thresholds
RISK_THRESHOLDS = {
    "CRITICAL": 0.30,
    "HIGH": 0.15,
    "MEDIUM": 0.05,
    "LOW": 0.0,
}

# Inventory status colors
STATUS_COLORS = {
    "CRITICAL": "#FF4444",
    "HIGH": "#FF8C00",
    "MEDIUM": "#FFD700",
    "LOW": "#00C851",
    "OK": "#00C851",
}
