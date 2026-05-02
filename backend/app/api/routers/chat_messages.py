from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.crud.crud_chat_message import create_chat_message, get_chat_messages_by_user
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_new_message(
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Store a new chat message (from user or Socratic Tutor).
    """
    if message_in.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return create_chat_message(db=db, message=message_in)

@router.get("/", response_model=List[ChatMessageResponse])
def read_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the chat history for the current user.
    """
    messages = get_chat_messages_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return messages
