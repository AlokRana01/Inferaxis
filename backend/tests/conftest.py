"""Pytest fixtures for Inferaxis backend tests."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from app.core.config import Settings
from app.main import create_app
from app.models.base import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# In-memory SQLite async test database URL
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_settings(tmp_path_factory: pytest.TempPathFactory) -> Settings:
    """Provide isolated test settings with SQLite async memory database and temp storage."""
    temp_storage = tmp_path_factory.mktemp("inferaxis_test_storage")
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        DATABASE_URL=TEST_DB_URL,
        ALLOWED_ORIGINS=["http://testserver"],
        STORAGE_PATH=str(temp_storage),
        DATASET_STORAGE_PATH=str(temp_storage / "datasets"),
    )


@pytest_asyncio.fixture(scope="function")
async def db_engine(test_settings: Settings):
    """Create test SQLite async database engine and initialize all tables."""
    engine = create_async_engine(test_settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session per test."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def async_client(
    test_settings: Settings, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Provide HTTP async test client for FastAPI application with isolated DB session and storage."""
    from app.api.v1.datasets import get_dataset_service
    from app.core.database import get_db
    from app.core.storage import LocalStorageService
    from app.services.dataset_service import DatasetService

    app = create_app(settings=test_settings)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_dataset_service] = lambda: DatasetService(
        storage_service=LocalStorageService(base_path=test_settings.STORAGE_PATH)
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
