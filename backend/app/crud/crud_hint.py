from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.hint import Hint
from app.schemas.hint import HintCreate

def get_hint(db: Session, hint_id: int) -> Optional[Hint]:
    """Get a hint by ID."""
    return db.execute(select(Hint).where(Hint.id == hint_id)).scalar_one_or_none()

def get_recent_hint_for_task(db: Session, task_id: int, user_id: int) -> Optional[Hint]:
    """
    Get the most recent hint for a user on a specific task.
    Used to avoid showing duplicate hints in the same session.
    """
    return db.execute(
        select(Hint)
        .where(Hint.task_id == task_id, Hint.user_id == user_id)
        .order_by(Hint.shown_at.desc())
    ).scalar_one_or_none()

def create_hint(db: Session, hint: HintCreate) -> Hint:
    """Create a new hint record."""
    db_hint = Hint(**hint.model_dump())
    db.add(db_hint)
    db.commit()
    db.refresh(db_hint)
    return db_hint

def dismiss_hint(db: Session, hint_id: int) -> Hint:
    """Mark a hint as dismissed by the user."""
    hint = get_hint(db, hint_id)
    if hint:
        hint.dismissed_at = datetime.utcnow()
        db.commit()
        db.refresh(hint)
    return hint
