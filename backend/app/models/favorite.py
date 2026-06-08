from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True) # Optional foreign key logic if needed: ForeignKey("users.id")
    item_type: Mapped[str] = mapped_column(index=True) # e.g., 'chat', 'lesson', 'code'
    item_content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
