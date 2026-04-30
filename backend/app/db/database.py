from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Assuming postgres runs locally or via docker-compose on default port
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5440/aicoach"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def init_db():
    # Import all models here so that Base has them registered before creation
    from app.models import (
        user,
        knowledge_source,
        journey,
        daily_plan,
        task,
        user_submission,
    )
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
