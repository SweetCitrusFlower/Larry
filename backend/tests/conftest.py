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
import pytest

# ── Set env vars BEFORE importing anything from the app ────────────────────
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

from sqlalchemy import create_engine, event                   # noqa: E402
from sqlalchemy.orm import sessionmaker                        # noqa: E402
from fastapi.testclient import TestClient                      # noqa: E402

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
