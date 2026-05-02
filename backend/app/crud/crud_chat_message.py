from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageCreate

def get_chat_message(db: Session, message_id: int) -> Optional[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

def get_chat_messages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp.asc()).offset(skip).limit(limit).all()

def create_chat_message(db: Session, message: ChatMessageCreate) -> ChatMessage:
    db_message = ChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_chat_message(db: Session, message_id: int) -> Optional[ChatMessage]:
    db_message = get_chat_message(db, message_id)
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message
