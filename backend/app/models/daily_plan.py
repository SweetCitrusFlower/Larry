from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.journey import Journey
    from app.models.task import Task

class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    journey_id: Mapped[int] = mapped_column(ForeignKey("journeys.id"))
    day_number: Mapped[int]
    title: Mapped[str] = mapped_column(String)
    concepts_to_cover: Mapped[list] = mapped_column(JSON)
    difficulty: Mapped[str] = mapped_column(String)
    theoretical_topic_content: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Retained for Content Creator AI
    rag_context_payload: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Retained for Socratic Tutor context inheritance
    completion_status: Mapped[bool] = mapped_column(default=False)
    content_status: Mapped[str] = mapped_column(String, default="PENDING")
    recommended_problem_tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Relationships
    journey: Mapped["Journey"] = relationship(back_populates="daily_plans")
    tasks: Mapped[List["Task"]] = relationship(back_populates="daily_plan", cascade="all, delete-orphan")
    