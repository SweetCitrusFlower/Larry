from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.journey import Journey
    from app.models.user_submission import UserSubmission

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    # Relationships
    journeys: Mapped[List["Journey"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[List["UserSubmission"]] = relationship(back_populates="user", cascade="all, delete-orphan")
