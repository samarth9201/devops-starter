import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock


# Shared fixture for all tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Unit test fixtures
@pytest.fixture
def mock_db():
    """Fixture for unit tests - returns a mock db session"""
    return AsyncMock(spec=AsyncSession)


# Integration test fixtures - only used when specifically requested
@pytest.fixture(scope="session")
async def integration_test_db():
    """Fixture for integration tests - creates real test database"""
    from src.database import DatabaseSession, Base
    from src.config import settings

    # Create a separate database instance for testing
    test_db = DatabaseSession()
    test_db.init(settings.DATABASE_URL)

    # Create tables
    engine = test_db._engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield test_db

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_db.close()


@pytest.fixture
async def integration_session(integration_test_db):
    """Fixture for integration tests - provides database session"""
    async for session in integration_test_db.get_session():
        yield session
        await session.close()


# API test fixtures
async def override_get_db():
    """Override for FastAPI dependency injection in integration tests"""
    from src.database import DatabaseSession, Base
    from src.config import settings

    test_db = DatabaseSession()
    test_db.init(settings.DATABASE_URL)

    async with test_db._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        async for session in test_db.get_session():
            yield session
    finally:
        await test_db.close()


@pytest.fixture
async def test_client():
    """Fixture for API integration tests"""
    from httpx import AsyncClient
    from src.main import app, get_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
