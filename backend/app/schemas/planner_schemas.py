from pydantic import BaseModel, Field
from typing import List, Literal

class DailyPlanItem(BaseModel):
    """
    Schema for a single day in the learning journey.
    """
    day_number: int = Field(..., description="The sequential day number of the plan.")
    title: str = Field(..., description="The main focus or topic for this day.")
    concepts_to_cover: List[str] = Field(..., description="A list of specific concepts or sub-topics to cover.")
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = Field(..., description="The difficulty level of the material for this day.")

class JourneyRoadmap(BaseModel):
    """
    Schema for the entire learning journey roadmap.
    """
    journey_title: str = Field(..., description="A catchy and descriptive title for the overall journey.")
    overview: str = Field(..., description="A brief overview of what the user will achieve by the end of this roadmap.")
    daily_plans: List[DailyPlanItem] = Field(..., description="The list of daily plans, ordered by day_number.")
