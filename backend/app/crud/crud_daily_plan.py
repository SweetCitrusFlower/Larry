from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.daily_plan import DailyPlan
from app.schemas.daily_plan import DailyPlanCreate, DailyPlanUpdate

def get_daily_plan(db: Session, daily_plan_id: int) -> Optional[DailyPlan]:
    return db.execute(select(DailyPlan).where(DailyPlan.id == daily_plan_id)).scalar_one_or_none()

def get_daily_plans_by_journey(db: Session, journey_id: int, skip: int = 0, limit: int = 100) -> List[DailyPlan]:
    return list(db.execute(select(DailyPlan).where(DailyPlan.journey_id == journey_id).offset(skip).limit(limit)).scalars().all())

def create_daily_plan(db: Session, daily_plan: DailyPlanCreate) -> DailyPlan:
    db_daily_plan = DailyPlan(**daily_plan.model_dump())
    db.add(db_daily_plan)
    db.commit()
    db.refresh(db_daily_plan)
    return db_daily_plan

def update_daily_plan(db: Session, db_daily_plan: DailyPlan, daily_plan_in: DailyPlanUpdate) -> DailyPlan:
    update_data = daily_plan_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_daily_plan, field, value)
    db.commit()
    db.refresh(db_daily_plan)
    return db_daily_plan

def delete_daily_plan(db: Session, db_daily_plan: DailyPlan) -> DailyPlan:
    db.delete(db_daily_plan)
    db.commit()
    return db_daily_plan
