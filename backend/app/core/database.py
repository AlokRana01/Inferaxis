"""Database connection management and async session provider."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

logger = logging.getLogger("inferaxis.database")
settings = get_settings()

# Engine creation parameters tailored for postgresql asyncpg vs sqlite aiosqlite
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if not settings.is_sqlite:
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
        }
    )

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for FastAPI route handlers."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection(target_engine: AsyncEngine | None = None) -> bool:
    """Verify database connectivity with a lightweight ping query."""
    active_engine = target_engine or engine
    try:
        async with active_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except (
        SQLAlchemyError,
        OSError,
        ConnectionError,
        RuntimeError,
        AttributeError,
    ) as exc:
        logger.warning("Database connection check failed: %s", exc)
        return False
