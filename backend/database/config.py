"""
Database configuration and connection management.

WHAT: Provides SQLAlchemy database engine configuration, session management,
      and connection utilities for the lead generation platform.

WHY: The application needs persistent storage for reference clients, campaigns,
     prospects, and search history. Centralized database configuration ensures
     consistent connection handling across the application.

HOW: Uses SQLAlchemy 2.0 with async support, configures PostgreSQL connection
     from environment variables, and provides session factory for dependency
     injection in FastAPI routes.

DEPENDENCIES:
- sqlalchemy: Database ORM and connection management
- os: Environment variable access for database URL
- typing: Type hints for better code documentation
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:password@localhost:5432/looklike_nearby"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_size=10,
    max_overflow=20,
)

# Session factory for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI routes.
    
    Creates a new database session for each request and ensures
    proper cleanup after the request completes.
    
    Yields:
        AsyncSession: Database session for the current request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in the models if they don't exist.
    This is typically called during application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 