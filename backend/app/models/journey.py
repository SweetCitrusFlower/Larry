from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.daily_plan import DailyPlan

class Journey(Base):
    __tablename__ = "journeys"
    # Composite index on original_prompt + target_days to speed up lookup for
    # repeated requests. Note: we perform case-insensitive, trimmed comparisons
    # in queries; creating a functional index (lower(trim(original_prompt)))
    # would be ideal for those lookups but requires a database migration each
    # target DB (and may be DB-specific). This simple composite index still
    # helps many lookups and is inexpensive to add.
    __table_args__ = (
        Index("ix_journeys_original_prompt_target_days", "original_prompt", "target_days"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_prompt: Mapped[str] = mapped_column(String)
    target_days: Mapped[int] = mapped_column(default=1)
    journey_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="journeys")
    daily_plans: Mapped[List["DailyPlan"]] = relationship(back_populates="journey", cascade="all, delete-orphan")
