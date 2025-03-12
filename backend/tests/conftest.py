"""Test configuration and fixtures."""

import os
import warnings
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock

# Set testing environment variable
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Suppress pkg_resources deprecation warning
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="pkg_resources is deprecated as an API",
)

from app.core.config import settings
from app.core.security import create_access_token, get_api_key, get_current_user
from app.database.session import get_db
from app.services.companion.service import CompanionService
from app.services.live2d.service import Live2DService
from app.services.tts.service import TTSService
from app.services.user.service import UserService
from main import app
from tests.mocks import (
    MockCompanionService,
    MockEmbeddingsService,
    MockLive2DService,
    MockTTSService,
    MockUserService,
)

# Import our test-specific models instead of app models
from tests.models import Base

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Create test engine with SQLite-specific settings
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure settings are properly configured for testing
assert settings.TESTING is True, "TESTING environment variable not properly set"
assert (
    settings.SQLALCHEMY_DATABASE_URI is not None
), "Test database URL not properly configured"


# Create a mock user class
class MockUser:
    """Mock User class with the attributes needed by the auth endpoints."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    """Create a fresh database on each test case."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with the test database."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    # Override the get_current_user dependency
    async def override_get_current_user():
        return {
            "id": 2,
            "email": "testuser@test.com",
            "role": "user",
            "is_active": True,
            "email_verified": True,
        }

    # Override the get_api_key dependency
    def override_get_api_key():
        return "test-api-key"

    # Add the overrides for authentication
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_api_key] = override_get_api_key

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Create and return an admin user token."""
    admin_data = {
        "sub": "1",  # User ID as string
        "email": "admin@test.com",
        "role": "admin",
        "exp": 9999999999,  # Far future expiration
    }
    return create_access_token(data=admin_data)


@pytest.fixture(scope="session")
def user_token() -> str:
    """Create and return a regular user token."""
    user_data = {
        "sub": "2",  # User ID as string
        "email": "testuser@test.com",
        "role": "user",
        "exp": 9999999999,  # Far future expiration
    }
    return create_access_token(data=user_data)


@pytest.fixture(scope="session")
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Return headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def user_headers(user_token: str) -> Dict[str, str]:
    """Return headers with user token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="session")
def test_user() -> Dict[str, Any]:
    """Return test user data."""
    return {
        "id": 2,
        "username": "testuser",
        "email": "testuser@test.com",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture(scope="session")
def test_admin() -> Dict[str, Any]:
    """Return test admin data."""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@test.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_user_service(monkeypatch):
    """Mock the user service for testing."""
    mock_service = MockUserService()
    monkeypatch.setattr("app.api.v1.endpoints.auth.UserService", lambda: mock_service)
    monkeypatch.setattr("app.api.v1.endpoints.users.UserService", lambda: mock_service)
    return mock_service


@pytest.fixture
def mock_tts_service(monkeypatch):
    """Mock the TTS service for testing."""
    mock_service = MockTTSService()
    monkeypatch.setattr("app.api.v1.endpoints.tts.TTSService", lambda: mock_service)
    return mock_service


@pytest.fixture
def mock_live2d_service(monkeypatch):
    """Mock the Live2D service for testing."""
    mock_service = MockLive2DService()
    monkeypatch.setattr(
        "app.api.v1.endpoints.live2d.Live2DService", lambda: mock_service
    )
    return mock_service


@pytest.fixture
def mock_companion_service(monkeypatch):
    """Mock the Companion service for testing."""
    mock_service = MockCompanionService()
    monkeypatch.setattr(
        "app.api.v1.endpoints.companions.CompanionService", lambda: mock_service
    )
    return mock_service


@pytest.fixture
def mock_embeddings_service(monkeypatch):
    """Mock the Embeddings service for testing."""
    mock_service = MockEmbeddingsService()
    monkeypatch.setattr(
        "app.services.knowledge.embeddings.embeddings_service", mock_service
    )
    return mock_service


@pytest.fixture
def mock_knowledge_service():
    """Mock the Knowledge service for testing."""
    mock_service = AsyncMock()
    mock_service.get_multi = AsyncMock()
    mock_service.count = AsyncMock()
    mock_service.get = AsyncMock()
    mock_service.create_with_relations = AsyncMock()
    mock_service.update_with_audit = AsyncMock()
    mock_service.delete = AsyncMock()
    mock_service.search_similar = AsyncMock()
    mock_service._generate_embedding = AsyncMock()

    return mock_service


@pytest.fixture
def mock_tag_service():
    """Mock the Tag service for testing."""
    mock_service = AsyncMock()
    mock_service.get_multi = AsyncMock()
    mock_service.create_with_validation = AsyncMock()

    return mock_service
