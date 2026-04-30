from pydantic import BaseModel, ConfigDict
from typing import Optional

class TaskBase(BaseModel):
    title: str
    problem_id: str
    description: str
    starter_code: str
    hidden_solution: str

class TaskCreate(TaskBase):
    daily_plan_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    starter_code: Optional[str] = None
    hidden_solution: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    daily_plan_id: int

    model_config = ConfigDict(from_attributes=True)
