"""
Database connection, session management, and base model.
Supports SQLite (development) and PostgreSQL (production).
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from erp_backend.config import get_settings


settings = get_settings()

# -----------------------------------------------------------------
# Engine creation
# -----------------------------------------------------------------
def _create_engine():
    db_url = settings.database_url
    if db_url.startswith("sqlite"):
        # SQLite-specific settings
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )
        # Enable WAL mode for better concurrent read performance
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.debug,
        )
    return engine


engine = _create_engine()

# -----------------------------------------------------------------
# Session factory
# -----------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -----------------------------------------------------------------
# Declarative base
# -----------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# -----------------------------------------------------------------
# Dependency — FastAPI DI
# -----------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for DB sessions (use outside FastAPI DI)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables():
    """Create all database tables (idempotent)."""
    # Import all models to register them with Base
    from erp_backend.models import (  # noqa: F401
        item, supplier, warehouse, inventory, inventory_ledger,
        purchase_order, goods_receipt, sales_order, sensor_log, forecast_cache
    )
    Base.metadata.create_all(bind=engine)
