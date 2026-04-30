from pydantic import BaseModel, ConfigDict
from typing import Optional

class DailyPlanBase(BaseModel):
    day_number: int
    theoretical_topic_content: str
    completion_status: Optional[bool] = False

class DailyPlanCreate(DailyPlanBase):
    journey_id: int

class DailyPlanUpdate(BaseModel):
    theoretical_topic_content: Optional[str] = None
    completion_status: Optional[bool] = None

class DailyPlanResponse(DailyPlanBase):
    id: int
    journey_id: int

    model_config = ConfigDict(from_attributes=True)
