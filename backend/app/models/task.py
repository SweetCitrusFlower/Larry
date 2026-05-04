from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.journey import DailyPlan
    from app.models.user_submission import UserSubmission

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    daily_plan_id: Mapped[int] = mapped_column(ForeignKey("daily_plans.id"))
    title: Mapped[str]
    problem_id: Mapped[str] # External ID from the open-source problem dataset
    description: Mapped[str] # Markdown description of the problem
    starter_code: Mapped[str]
    hidden_solution: Mapped[str]

    # Relationships
    daily_plan: Mapped["DailyPlan"] = relationship(back_populates="tasks")
    submissions: Mapped[List["UserSubmission"]] = relationship(back_populates="task", cascade="all, delete-orphan")
