from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.journey import Journey
from app.schemas.journey import JourneyCreate, JourneyUpdate

def get_journey(db: Session, journey_id: int) -> Optional[Journey]:
    return db.execute(select(Journey).where(Journey.id == journey_id)).scalar_one_or_none()

def get_journeys_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Journey]:
    return list(db.execute(select(Journey).where(Journey.user_id == user_id).offset(skip).limit(limit)).scalars().all())

def create_journey(db: Session, journey: JourneyCreate) -> Journey:
    db_journey = Journey(**journey.model_dump())
    db.add(db_journey)
    db.commit()
    db.refresh(db_journey)
    return db_journey

def update_journey(db: Session, db_journey: Journey, journey_in: JourneyUpdate) -> Journey:
    update_data = journey_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_journey, field, value)
    db.commit()
    db.refresh(db_journey)
    return db_journey

def delete_journey(db: Session, db_journey: Journey) -> Journey:
    db.delete(db_journey)
    db.commit()
    return db_journey
