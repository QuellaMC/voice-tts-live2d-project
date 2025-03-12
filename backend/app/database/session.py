"""Database session management."""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator

from app.core.config import settings
from app.core.monitoring import record_db_operation
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


# Create engine configuration based on database type
def get_engine_args() -> Dict[str, Any]:
    """Get database engine arguments based on database type."""
    if (
        settings.TESTING
        and settings.SQLALCHEMY_DATABASE_URI
        and "sqlite" in settings.SQLALCHEMY_DATABASE_URI
    ):
        # SQLite-specific configuration
        return {
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            # SQLite doesn't support these options
            # "pool_size": settings.DB_POOL_SIZE,
            # "max_overflow": settings.DB_MAX_OVERFLOW,
            # "pool_timeout": settings.DB_POOL_TIMEOUT,
        }
    else:
        # PostgreSQL configuration
        return {
            "pool_pre_ping": True,
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
        }


# Create database engine with appropriate connection pooling
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, **get_engine_args())

# Create sessionmaker with class-wide scope
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(
    conn: Any,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: bool,
) -> None:
    """Event listener to track database operation timing."""
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(
    conn: Any,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: bool,
) -> None:
    """Event listener to record database operation metrics."""
    total = time.time() - conn.info["query_start_time"].pop(-1)
    # Extract operation type and table from the statement
    operation = statement.split()[0].lower()
    table = statement.split()[2] if len(statement.split()) > 2 else "unknown"
    record_db_operation(operation, table, total)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def check_db_connection() -> bool:
    """Check database connection with retry logic."""
    try:
        # Try to connect and execute a simple query
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


def cleanup_db() -> None:
    """Cleanup database resources on application shutdown."""
    try:
        engine.dispose()
        logger.info("Database connections cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")


# Initialize connection pool on startup
def init_db() -> None:
    """Initialize database connection pool."""
    try:
        check_db_connection()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
