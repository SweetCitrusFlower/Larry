from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserSubmissionBase(BaseModel):
    submitted_code: str
    language_id: Optional[int] = 71
    score: Optional[float] = None
    result_status: str

class UserSubmissionCreate(UserSubmissionBase):
    user_id: int
    task_id: int

class UserSubmissionUpdate(BaseModel):
    score: Optional[float] = None
    result_status: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None

class UserSubmissionResponse(UserSubmissionBase):
    id: int
    user_id: int
    task_id: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
