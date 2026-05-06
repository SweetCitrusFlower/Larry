from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task

class UserSubmission(Base):
    __tablename__ = "user_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    language_id: Mapped[Optional[int]] = mapped_column(default=71) # e.g., 71 for Python 3
    submitted_code: Mapped[str]
    stdout: Mapped[Optional[str]]
    stderr: Mapped[Optional[str]]
    execution_time: Mapped[Optional[float]]
    memory_usage: Mapped[Optional[int]]
    score: Mapped[Optional[float]] # e.g., percentage of test cases passed
    result_status: Mapped[str] # e.g., pending, accepted, wrong_answer, compile_error

    # Relationships
    user: Mapped["User"] = relationship(back_populates="submissions")
    task: Mapped["Task"] = relationship(back_populates="submissions")
