from pydantic import BaseModel, Field
from typing import List, Literal

class TaskItem(BaseModel):
    problem_title: str = Field(..., description="The title of the practical task or problem.")
    problem_description: str = Field(..., description="A detailed markdown description of the problem.")
    starter_code: str = Field(..., description="The starter code snippet for the user to begin with.")
    hidden_solution: str = Field(..., description="The complete, working solution code for the problem.")

class DailyPlanItem(BaseModel):
    """
    Schema for a single day in the learning journey.
    """
    day_number: int = Field(..., description="The sequential day number of the plan.")
    title: str = Field(..., description="The main focus or topic for this day.")
    concepts_to_cover: List[str] = Field(..., description="A list of specific concepts or sub-topics to cover.")
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = Field(..., description="The difficulty level of the material for this day.")
    theoretical_topic_content: str = Field(..., description="Comprehensive theoretical content explaining the concepts for the day. Use markdown.")
    task: TaskItem = Field(..., description="A practical coding task or exercise applying the day's concepts.")
    recommended_problem_tags: List[str] = Field(..., description="Select up to 3 tags strictly from the provided unique tags list.")

class JourneyRoadmap(BaseModel):
    """
    Schema for the entire learning journey roadmap.
    """
    journey_title: str = Field(..., description="A catchy and descriptive title for the overall journey.")
    overview: str = Field(..., description="A brief overview of what the user will achieve by the end of this roadmap.")
    daily_plans: List[DailyPlanItem] = Field(..., description="The list of daily plans, ordered by day_number.")
