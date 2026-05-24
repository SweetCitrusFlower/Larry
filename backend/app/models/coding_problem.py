from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class CodingProblem(Base):
    """
    An independent, global pool of coding problems.
    These are decoupled from specific users or daily plans.
    The Content Creator agent will pull from here and create a `Task` 
    for a specific `DailyPlan`.
    """
    __tablename__ = "coding_problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    problem_id: Mapped[str] = mapped_column(unique=True, index=True) # e.g., mbpp_12
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    tags: Mapped[list] = mapped_column(JSON)
    starter_code: Mapped[str] = mapped_column(String)
    hidden_solution: Mapped[str] = mapped_column(String) # For Judge0 testing context
