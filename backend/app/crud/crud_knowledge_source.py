from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.knowledge_source import KnowledgeSource
from app.schemas.knowledge_source import KnowledgeSourceCreate, KnowledgeSourceUpdate

def get_knowledge_source(db: Session, source_id: int) -> Optional[KnowledgeSource]:
    return db.execute(select(KnowledgeSource).where(KnowledgeSource.id == source_id)).scalar_one_or_none()

def get_knowledge_sources(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[KnowledgeSource]:
    return list(db.execute(select(KnowledgeSource).where(KnowledgeSource.user_id == user_id).offset(skip).limit(limit)).scalars().all())

def create_knowledge_source(db: Session, source: KnowledgeSourceCreate) -> KnowledgeSource:
    db_source = KnowledgeSource(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def update_knowledge_source(db: Session, db_source: KnowledgeSource, source_in: KnowledgeSourceUpdate) -> KnowledgeSource:
    update_data = source_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)
    db.commit()
    db.refresh(db_source)
    return db_source

def delete_knowledge_source(db: Session, db_source: KnowledgeSource) -> KnowledgeSource:
    db.delete(db_source)
    db.commit()
    return db_source
