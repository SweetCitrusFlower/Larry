from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserSubmissionBase(BaseModel):
    submitted_code: str
    score: Optional[float] = None
    result_status: str

class UserSubmissionCreate(UserSubmissionBase):
    user_id: int
    task_id: int

class UserSubmissionUpdate(BaseModel):
    score: Optional[float] = None
    result_status: Optional[str] = None

class UserSubmissionResponse(UserSubmissionBase):
    id: int
    user_id: int
    task_id: int

    model_config = ConfigDict(from_attributes=True)
