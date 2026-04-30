from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.daily_plan import DailyPlan

class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    initial_user_prompt: Mapped[str]
    objectives: Mapped[str] # Could be stored as JSON, using string for simplicity initially
    start_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    total_days: Mapped[int]
    status: Mapped[str] = mapped_column(default="active") # active, completed, abandoned

    # Relationships
    user: Mapped["User"] = relationship(back_populates="journeys")
    daily_plans: Mapped[List["DailyPlan"]] = relationship(back_populates="journey", cascade="all, delete-orphan")
