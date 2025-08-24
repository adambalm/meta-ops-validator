"""
Database engine configuration supporting SQLite and PostgreSQL
"""
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from typing import Optional

from ..models import Base


def get_database_url() -> str:
    """
    Get database URL from environment or default to SQLite.
    
    Environment variables:
    - DATABASE_URL: Full database URL (overrides all others)
    - DB_TYPE: "sqlite" or "postgresql" 
    - DB_PATH: Path for SQLite database (default: data/demo.db)
    - POSTGRES_URL: PostgreSQL connection string
    """
    # Check for explicit DATABASE_URL first
    if database_url := os.getenv("DATABASE_URL"):
        return database_url
    
    # Check database type preference
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "postgresql":
        postgres_url = os.getenv(
            "POSTGRES_URL", 
            "postgresql+asyncpg://postgres:password@localhost/metaops_demo"
        )
        return postgres_url
    
    # Default to SQLite
    db_path = os.getenv("DB_PATH", "data/demo.db")
    
    # Ensure directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    return f"sqlite+aiosqlite:///{db_path}"


def create_database_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """
    Create async SQLAlchemy engine with appropriate configuration.
    
    Args:
        database_url: Database URL. If None, gets from environment.
        
    Returns:
        Configured AsyncEngine instance
    """
    if database_url is None:
        database_url = get_database_url()
    
    # SQLite-specific configuration
    if database_url.startswith("sqlite"):
        engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            future=True,
            # SQLite specific settings
            pool_pre_ping=True,
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
    else:
        # PostgreSQL configuration
        engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging  
            future=True,
            # PostgreSQL specific settings
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    
    return engine


async def create_tables(engine: AsyncEngine) -> None:
    """
    Create all database tables.
    
    Args:
        engine: Database engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine) -> None:
    """
    Drop all database tables (useful for testing).
    
    Args:
        engine: Database engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory.
    
    Args:
        engine: Database engine
        
    Returns:
        Session factory
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


# Global engine and session factory (initialized on first import)
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """Get global database engine, creating it if needed."""
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get global session factory, creating it if needed."""
    global _session_factory
    if _session_factory is None:
        _session_factory = create_session_factory(get_engine())
    return _session_factory


async def get_async_session() -> AsyncSession:
    """
    Get async database session.
    
    Usage:
        async with get_async_session() as session:
            # Use session
            pass
    """
    factory = get_session_factory()
    return factory()


async def init_database() -> None:
    """Initialize database by creating all tables."""
    engine = get_engine()
    await create_tables(engine)