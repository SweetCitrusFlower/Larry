from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class DailyPlanResponse(BaseModel):
    id: int
    journey_id: int
    day_number: int
    title: str
    concepts_to_cover: List[str]
    difficulty: str
    completion_status: bool = False
    model_config = ConfigDict(from_attributes=True)

class JourneyGenerateRequest(BaseModel):
    prompt: str
    target_days: int

class JourneyModifyRequest(BaseModel):
    prompt: str

class JourneyCreate(BaseModel):
    user_id: int
    original_prompt: str
    target_days: int
    journey_title: Optional[str] = None
    overview: Optional[str] = None

class JourneyUpdate(BaseModel):
    journey_title: Optional[str] = None
    overview: Optional[str] = None

class JourneyResponse(BaseModel):
    id: int
    user_id: int
    original_prompt: str
    target_days: int
    journey_title: Optional[str] = None
    overview: Optional[str] = None
    created_at: datetime
    daily_plans: List[DailyPlanResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
