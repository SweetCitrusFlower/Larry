from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.daily_plan import DailyPlan

class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_prompt: Mapped[str] = mapped_column(String)
    target_days: Mapped[int] = mapped_column(default=1)
    journey_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="journeys")
    daily_plans: Mapped[List["DailyPlan"]] = relationship(back_populates="journey", cascade="all, delete-orphan")
