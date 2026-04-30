from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    processing_status: Mapped[str] = mapped_column(default="pending") # e.g., pending, processing, completed, failed
    reference_id: Mapped[Optional[str]] = mapped_column(index=True) # ID referencing the document in ChromaDB
