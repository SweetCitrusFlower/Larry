from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class DailyPlanBase(BaseModel):
    day_number: int
    title: str
    concepts_to_cover: List[str]
    difficulty: str
    theoretical_topic_content: Optional[str] = None
    completion_status: bool = False
    content_status: str = "PENDING"
    recommended_problem_tags: Optional[List[str]] = None

class DailyPlanCreate(DailyPlanBase):
    journey_id: int

class DailyPlanUpdate(BaseModel):
    theoretical_topic_content: Optional[str] = None
    completion_status: bool = False
    content_status: str = "PENDING"

class DailyPlanResponse(DailyPlanBase):
    id: int
    journey_id: int
    day_number: int
    title: str
    concepts_to_cover: List[str]
    difficulty: str
    model_config = ConfigDict(from_attributes=True)
    
    recommended_problem_tags: List[str]
    theoretical_topic_content: str
    completion_status: bool
    content_status: str

# Schema for the AI Master Planner to ensure structured output
class PlannerDayOutput(BaseModel):
    day_number: int
    topics: str
    theoretical_topic_summary: str
    problem_title: str
    problem_description: str
    problem_starter_code: str
    problem_hidden_solution: str

class PlannerJourneyOutput(BaseModel):
    title: str
    objectives: str
    total_days: int
    days: List[PlannerDayOutput]
