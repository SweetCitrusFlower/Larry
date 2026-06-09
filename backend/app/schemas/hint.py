from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class HintBase(BaseModel):
    hint_text: str

class HintCreate(HintBase):
    task_id: int
    user_id: int

class HintResponse(HintBase):
    id: int
    task_id: int
    user_id: int
    shown_at: datetime
    dismissed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class HintGenerateRequest(BaseModel):
    """Request to generate an idle assistance hint for a task."""
    task_id: int
    user_id: int
    current_code: Optional[str] = None  # Current code state to provide context
