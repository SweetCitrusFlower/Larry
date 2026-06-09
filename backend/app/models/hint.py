from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User

class Hint(Base):
    """Tracks idle assistance hints shown to users to avoid duplicates."""
    __tablename__ = "hints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hint_text: Mapped[str]
    shown_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    task: Mapped["Task"] = relationship()
    user: Mapped["User"] = relationship()
