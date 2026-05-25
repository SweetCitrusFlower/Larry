from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import asyncio

from app.db.database import get_db
from app.models.user import User
from app.schemas.knowledge_source import KnowledgeSourceCreate, KnowledgeSourceUpdate, KnowledgeSourceResponse
from app.crud.crud_knowledge_source import get_knowledge_source, get_knowledge_sources, create_knowledge_source, update_knowledge_source, delete_knowledge_source
from app.api.deps import get_current_user

from app.services.vision_parser.extractor import extract_text_from_pdf
from app.services.vision_parser.chunker import chunk_markdown
from app.services.vision_parser.vector_store import store_chunks_in_chroma

router = APIRouter()

@router.post("/upload", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_source(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ALLOWED_TYPES = [
        "application/pdf", 
        "text/plain", 
        "text/markdown", 
        "text/x-python",
        "application/x-python-code"
    ]
    
    # Also check file extension as fallback since some clients send generic mimetypes for .py
    is_code_ext = file.filename.endswith(".py")
    
    if file.content_type not in ALLOWED_TYPES and not is_code_ext:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, MD, and PY files are supported.")
    
    # Create the record as 'pending'
    source_in = KnowledgeSourceCreate(title=file.filename, processing_status="pending", user_id=current_user.id)
    db_source = await asyncio.to_thread(create_knowledge_source, db, source=source_in)
    
    try:
        # Read the file
        file_bytes = await file.read()
        
        # Extract markdown/text depending on type
        if file.content_type == "application/pdf":
            markdown_text = await extract_text_from_pdf(file_bytes)
        else:
            # Treat as plain text/code
            markdown_text = file_bytes.decode('utf-8')
            if is_code_ext or 'python' in file.content_type:
                # Wrap code in markdown block for better chunking and readability
                markdown_text = f"```python\n{markdown_text}\n```"
        
        # Chunk the text (offloaded to threadpool)
        chunks = await asyncio.to_thread(chunk_markdown, markdown_text)
        
        # Store in ChromaDB
        await store_chunks_in_chroma(chunks, file.filename)
        
        # Update status to completed
        source_update = KnowledgeSourceUpdate(processing_status="completed")
        return await asyncio.to_thread(update_knowledge_source, db, db_source=db_source, source_in=source_update)
    except Exception as e:
        # Update status to failed
        source_update = KnowledgeSourceUpdate(processing_status="failed")
        await asyncio.to_thread(update_knowledge_source, db, db_source=db_source, source_in=source_update)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@router.post("/", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
def create_new_knowledge_source(
    *,
    db: Session = Depends(get_db),
    source_in: KnowledgeSourceCreate,
    current_user: User = Depends(get_current_user)
):
    source_in.user_id = current_user.id
    return create_knowledge_source(db, source=source_in)

@router.get("/", response_model=List[KnowledgeSourceResponse])
def read_knowledge_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    # Depending on requirements, we could filter by user_id. The T0 baseline implies strict ownership.
    return get_knowledge_sources(db, skip=skip, limit=limit, user_id=current_user.id)

@router.get("/{source_id}", response_model=KnowledgeSourceResponse)
def read_knowledge_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source = get_knowledge_source(db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Source not found")
    if getattr(source, "user_id", None) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
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
    if getattr(source, "user_id", None) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
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
    if getattr(source, "user_id", None) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return delete_knowledge_source(db, db_source=source)
