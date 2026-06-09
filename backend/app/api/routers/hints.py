"""
Hints Router - Idle Assistance API endpoints

Provides endpoints for generating and managing idle assistance hints
for students stuck on coding tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.hint import Hint
from app.crud.crud_hint import create_hint, get_recent_hint_for_task, dismiss_hint
from app.schemas.hint import HintResponse, HintGenerateRequest, HintCreate
from app.services.idle_hint_service import generate_idle_hint

router = APIRouter()


@router.post("/generate-hint", response_model=HintResponse)
async def generate_hint(
    request: HintGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an idle assistance hint for a student.
    
    Generates a context-aware, Socratic hint to guide a student who has been
    inactive for 4+ minutes on a coding task. Hints are personalized based on:
    - Task description and difficulty
    - Concepts to learn for the day
    - Student's current code progress
    - RAG context from the daily plan
    
    Prevents duplicate hints by checking recent hint history.
    """
    # Verify the user is working on this task (access control)
    task = db.execute(select(Task).where(Task.id == request.task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check if a recent hint was already shown (avoid spam)
    recent_hint = get_recent_hint_for_task(db, request.task_id, current_user.id)
    if recent_hint and not recent_hint.dismissed_at:
        # Return the recent hint instead of generating a new one
        return recent_hint
    
    # Generate new hint
    hint_text = await generate_idle_hint(
        db=db,
        task_id=request.task_id,
        current_code=request.current_code
    )
    
    # Store hint in database
    hint_create = HintCreate(
        task_id=request.task_id,
        user_id=current_user.id,
        hint_text=hint_text
    )
    hint = create_hint(db, hint_create)
    
    return hint


@router.patch("/dismiss-hint/{hint_id}")
async def dismiss_hint_endpoint(
    hint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a hint as dismissed by the user.
    Used for tracking user interactions with idle assistance.
    """
    hint = db.execute(
        select(Hint).where(Hint.id == hint_id)
    ).scalar_one_or_none()
    
    if not hint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hint not found")
    
    # Verify ownership
    if hint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    updated_hint = dismiss_hint(db, hint_id)
    return {"status": "dismissed", "hint_id": updated_hint.id}
