"""
conftest.py
Pytest fixtures shared across all tests.

Root fix strategy:
- Patch db_module.engine & SessionLocal at module-level to point to SQLite.
- `setup_test_db` fixture (autouse, session-scoped) creates tables ONCE
  and drops them at the end of the test session, sharing the same connection.
- `client` fixture overrides get_db with a fresh TestingSessionLocal session
  per test, rolling back after each test to ensure isolation.
"""
import os
import sys
import pytest

def pytest_addoption(parser):
    parser.addoption("--live-evals", action="store_true", default=False, help="Run live evaluations using real LLM API calls")

LIVE_EVALS = "--live-evals" in sys.argv
if LIVE_EVALS:
    os.environ["LARRY_EVAL_MODE"] = "live"
else:
    os.environ["LARRY_EVAL_MODE"] = "mock"

# ── Set env vars BEFORE importing anything from the app ────────────────────
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

from sqlalchemy import create_engine, event                   # noqa: E402
from sqlalchemy.orm import sessionmaker                        # noqa: E402
from fastapi.testclient import TestClient                      # noqa: E402

import sys
from unittest.mock import MagicMock

# Mock out heavy and external dependencies to ensure tests run offline
sys.modules['weasyprint'] = MagicMock()
if not LIVE_EVALS:
    sys.modules['langchain_ollama'] = MagicMock()
    
    # Create a proper mock for VertexAI to support async embedding
    from unittest.mock import AsyncMock
    mock_vertexai = MagicMock()
    mock_embeddings_class = MagicMock()
    mock_embeddings_instance = MagicMock()
    mock_embeddings_instance.aembed_query = AsyncMock(return_value=[0.1] * 768)
    mock_embeddings_class.return_value = mock_embeddings_instance
    mock_vertexai.VertexAIEmbeddings = mock_embeddings_class
    
    sys.modules['langchain_google_vertexai'] = mock_vertexai
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['chromadb'] = MagicMock()

import app.db.database as db_module                            # noqa: E402
from app.db.database import Base, get_db                       # noqa: E402
from app.main import app                                       # noqa: E402

# Import all models so SQLAlchemy registers them on Base.metadata
from app.models import (                                       # noqa: E402, F401
    user, knowledge_source, journey, task, user_submission
)

# ── Single in-memory engine shared across the whole test session ─────────────
# Using a named in-memory DB and check_same_thread=False for SQLite compatibility
TEST_DB_URL = "sqlite:///file::memory:?cache=shared&uri=true"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False, "uri": True},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ── Patch the app's engine and SessionLocal to use our SQLite engine ─────────
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once at the start of the test session, drop at the end."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def reset_tables():
    """
    Clean all table data between tests without dropping/recreating schema.
    This is much faster than drop_all/create_all per test.
    """
    yield
    # After each test, delete all rows from every table in reverse dependency order
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture(scope="function")
def client():
    """
    Returns a FastAPI TestClient that uses SQLite via the patched engine.
    Dependency override ensures every request gets a fresh SQLite session.
    """
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db():
    """Yields a test database session for CRUD operations."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
