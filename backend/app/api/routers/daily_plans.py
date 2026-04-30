from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.daily_plan import DailyPlanCreate, DailyPlanUpdate, DailyPlanResponse
from app.crud.crud_daily_plan import get_daily_plan, get_daily_plans_by_journey, create_daily_plan, update_daily_plan, delete_daily_plan
from app.crud.crud_journey import get_journey
from app.api.deps import get_current_user

router = APIRouter()

def verify_journey_owner(db: Session, journey_id: int, user_id: int):
    journey = get_journey(db, journey_id=journey_id)
    if not journey or journey.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return journey

@router.post("/", response_model=DailyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_new_daily_plan(
    *,
    db: Session = Depends(get_db),
    daily_plan_in: DailyPlanCreate,
    current_user: User = Depends(get_current_user)
):
    verify_journey_owner(db, daily_plan_in.journey_id, current_user.id)
    return create_daily_plan(db, daily_plan=daily_plan_in)

@router.get("/journey/{journey_id}", response_model=List[DailyPlanResponse])
def read_journey_daily_plans(
    journey_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    verify_journey_owner(db, journey_id, current_user.id)
    return get_daily_plans_by_journey(db, journey_id=journey_id, skip=skip, limit=limit)

@router.get("/{daily_plan_id}", response_model=DailyPlanResponse)
def read_daily_plan(
    daily_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    daily_plan = get_daily_plan(db, daily_plan_id=daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Plan not found")
    verify_journey_owner(db, daily_plan.journey_id, current_user.id)
    return daily_plan

@router.put("/{daily_plan_id}", response_model=DailyPlanResponse)
def update_existing_daily_plan(
    daily_plan_id: int,
    daily_plan_in: DailyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    daily_plan = get_daily_plan(db, daily_plan_id=daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Plan not found")
    verify_journey_owner(db, daily_plan.journey_id, current_user.id)
    return update_daily_plan(db, db_daily_plan=daily_plan, daily_plan_in=daily_plan_in)

@router.delete("/{daily_plan_id}", response_model=DailyPlanResponse)
def delete_existing_daily_plan(
    daily_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    daily_plan = get_daily_plan(db, daily_plan_id=daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Plan not found")
    verify_journey_owner(db, daily_plan.journey_id, current_user.id)
    return delete_daily_plan(db, db_daily_plan=daily_plan)
