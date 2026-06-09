from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.crud.crud_chat_message import create_chat_message, get_chat_messages_by_user
from app.api.deps import get_current_user
from app.models.daily_plan import DailyPlan
from app.services.socratic_tutor import get_socratic_hint

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
    journey_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the chat history for the current user.
    """
    messages = get_chat_messages_by_user(db, user_id=current_user.id, skip=skip, limit=limit, journey_id=journey_id)
    return messages

@router.post("/{daily_plan_id}/hint", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def request_socratic_hint(
    daily_plan_id: int,
    user_query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint for users to request a hint from the Socratic Tutor.
    It inherits the RAG context from the given daily plan.
    """
    # 1. Fetch DailyPlan and Verify
    daily_plan = db.query(DailyPlan).filter(DailyPlan.id == daily_plan_id).first()
    if not daily_plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
        
    # Security: ensure daily plan belongs to current user's journey
    if daily_plan.journey.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this daily plan")

    # 2. Get the RAG context inherited from Master Planner / Content Creator
    rag_context = daily_plan.rag_context_payload or ""

    # 3. Call Socratic Tutor Service
    tutor_response_text = await get_socratic_hint(user_query=user_query, rag_context=rag_context)

    # 4. Save User's Message
    user_msg_in = ChatMessageCreate(
        role="user",
        content=user_query,
        user_id=current_user.id,
        daily_plan_id=daily_plan_id
    )
    create_chat_message(db=db, message=user_msg_in)

    # 5. Save and Return Tutor's Response
    tutor_msg_in = ChatMessageCreate(
        role="assistant",
        content=tutor_response_text,
        user_id=current_user.id,
        daily_plan_id=daily_plan_id
    )
    return create_chat_message(db=db, message=tutor_msg_in)

