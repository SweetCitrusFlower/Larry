import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Use DATABASE_URL env var if set (e.g., SQLite for tests), otherwise default to PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5440/aicoach",
)

# SQLite needs check_same_thread=False; PostgreSQL does not support that kwarg
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def init_db():
    # Skip DB initialization during automated tests (SQLite in-memory is managed by conftest.py)
    if os.getenv("TESTING") == "true":
        return
    # Import all models here so that Base has them registered before creation
    from app.models import (
        user,
        knowledge_source,
        journey,
        task,
        user_submission,
        chat_message,
    )
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
