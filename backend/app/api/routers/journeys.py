from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.journey import Journey, DailyPlan
from app.agents.master_planner import generate_roadmap

router = APIRouter()

class JourneyGenerateRequest(BaseModel):
    """
    Schema for the journey generation request.
    """
    prompt: str
    target_days: int

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_new_journey(
    request: JourneyGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to generate a new learning journey using the Master Planner AI Agent.
    """
    if request.target_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Target days must be a positive integer."
        )

    try:
        # 1. Call the AI Agent to generate the structured roadmap
        roadmap = await generate_roadmap(request.prompt, request.target_days)
        
        # 2. Map the roadmap to SQLAlchemy models
        db_journey = Journey(
            user_id=current_user.id,
            original_prompt=request.prompt,
            target_days=request.target_days,
            journey_title=roadmap.journey_title,
            overview=roadmap.overview
        )
        db.add(db_journey)
        
        # We flush to obtain the journey ID for the foreign keys in DailyPlan
        db.flush()
        
        # 3. Create DailyPlan objects for each day in the roadmap
        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty
            )
            db.add(db_plan)
        
        # 4. Commit everything to the database
        db.commit()
        db.refresh(db_journey)
        
        return db_journey

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        # Log the error here in a production environment
        print(f"Error during journey generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during journey generation: {str(e)}"
        )
