from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.journey import Journey
from app.models.daily_plan import DailyPlan
from app.agents.master_planner import generate_roadmap

router = APIRouter()

# ── Response schemas ──────────────────────────────────────────────────────────

class DailyPlanResponse(BaseModel):
    id: int
    journey_id: int
    day_number: int
    title: str
    concepts_to_cover: List[str]
    difficulty: str
    model_config = ConfigDict(from_attributes=True)

class JourneyResponse(BaseModel):
    id: int
    user_id: int
    original_prompt: str
    target_days: int
    journey_title: Optional[str]
    overview: Optional[str]
    created_at: datetime
    daily_plans: List[DailyPlanResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ── Request schema ─────────────────────────────────────────────────────────────

class JourneyGenerateRequest(BaseModel):
    prompt: str
    target_days: int

# ── Endpoints ──────────────────────────────────────────────────────────────────

from sqlalchemy import select

@router.get("/", response_model=List[JourneyResponse])
def list_journeys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all journeys (with daily plans) for the current user.
    """
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.user_id == current_user.id)
        .order_by(Journey.created_at.desc())
    )
    journeys = db.execute(stmt).scalars().unique().all()
    return journeys

@router.get("/{journey_id}", response_model=JourneyResponse)
def get_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a single journey with its daily plans.
    """
    stmt = (
        select(Journey)
        .options(joinedload(Journey.daily_plans))
        .where(Journey.id == journey_id, Journey.user_id == current_user.id)
    )
    journey = db.execute(stmt).scalars().unique().first()
    
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey

@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=JourneyResponse)
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
        roadmap = await generate_roadmap(request.prompt, request.target_days)
        
        db_journey = Journey(
            user_id=current_user.id,
            original_prompt=request.prompt,
            target_days=request.target_days,
            journey_title=roadmap.journey_title,
            overview=roadmap.overview
        )
        db.add(db_journey)
        db.flush()
        
        for plan_item in roadmap.daily_plans:
            db_plan = DailyPlan(
                journey_id=db_journey.id,
                day_number=plan_item.day_number,
                title=plan_item.title,
                concepts_to_cover=plan_item.concepts_to_cover,
                difficulty=plan_item.difficulty
            )
            db.add(db_plan)
        
        db.commit()

        # Re-query with eager load so daily_plans are included in response
        db.refresh(db_journey)
        journey = (
            db.query(Journey)
            .options(joinedload(Journey.daily_plans))
            .filter(Journey.id == db_journey.id)
            .first()
        )
        return journey

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"Error during journey generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during journey generation: {str(e)}"
        )
