from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class JourneyBase(BaseModel):
    title: str
    initial_user_prompt: str
    objectives: str
    total_days: int
    status: Optional[str] = "active"

class JourneyCreate(JourneyBase):
    user_id: int

class JourneyUpdate(BaseModel):
    title: Optional[str] = None
    objectives: Optional[str] = None
    status: Optional[str] = None

class JourneyResponse(JourneyBase):
    id: int
    user_id: int
    start_date: datetime

    model_config = ConfigDict(from_attributes=True)
