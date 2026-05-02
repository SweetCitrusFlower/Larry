from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.journey import DailyPlan
    from app.models.user import User

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Linked to a daily plan (specific context) or a user session (general)
    daily_plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("daily_plans.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    role: Mapped[str] = mapped_column(String(20)) # "user", "assistant", "system"
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    daily_plan: Mapped[Optional["DailyPlan"]] = relationship()
    user: Mapped["User"] = relationship()
