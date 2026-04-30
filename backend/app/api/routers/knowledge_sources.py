from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.knowledge_source import KnowledgeSourceCreate, KnowledgeSourceUpdate, KnowledgeSourceResponse
from app.crud.crud_knowledge_source import get_knowledge_source, get_knowledge_sources, create_knowledge_source, update_knowledge_source, delete_knowledge_source
from app.api.deps import get_current_user

router = APIRouter()

# Assuming knowledge sources are global (like an admin uploads books).
# Alternatively, could be user-specific. We'll make them global but require authentication.

@router.post("/", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
def create_new_knowledge_source(
    *,
    db: Session = Depends(get_db),
    source_in: KnowledgeSourceCreate,
    current_user: User = Depends(get_current_user)
):
    # Depending on requirements, might want to restrict this to 'admin' users.
    return create_knowledge_source(db, source=source_in)

@router.get("/", response_model=List[KnowledgeSourceResponse])
def read_knowledge_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    return get_knowledge_sources(db, skip=skip, limit=limit)

@router.get("/{source_id}", response_model=KnowledgeSourceResponse)
def read_knowledge_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source = get_knowledge_source(db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Source not found")
    return source

@router.put("/{source_id}", response_model=KnowledgeSourceResponse)
def update_existing_knowledge_source(
    source_id: int,
    source_in: KnowledgeSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source = get_knowledge_source(db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Source not found")
    return update_knowledge_source(db, db_source=source, source_in=source_in)

@router.delete("/{source_id}", response_model=KnowledgeSourceResponse)
def delete_existing_knowledge_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source = get_knowledge_source(db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Source not found")
    return delete_knowledge_source(db, db_source=source)
