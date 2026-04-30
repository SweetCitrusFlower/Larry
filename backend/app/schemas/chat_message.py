from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ChatMessageBase(BaseModel):
    role: str # "user", "assistant", "system"
    content: str
    daily_plan_id: Optional[int] = None

class ChatMessageCreate(ChatMessageBase):
    user_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
