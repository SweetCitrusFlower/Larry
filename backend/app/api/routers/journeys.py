from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.journey import JourneyCreate, JourneyUpdate, JourneyResponse
from app.crud.crud_journey import get_journey, get_journeys_by_user, create_journey, update_journey, delete_journey
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=JourneyResponse, status_code=status.HTTP_201_CREATED)
def create_new_journey(
    *,
    db: Session = Depends(get_db),
    journey_in: JourneyCreate,
    current_user: User = Depends(get_current_user)
):
    if journey_in.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return create_journey(db, journey=journey_in)

@router.get("/", response_model=List[JourneyResponse])
def read_user_journeys(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    return get_journeys_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{journey_id}", response_model=JourneyResponse)
def read_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    journey = get_journey(db, journey_id=journey_id)
    if not journey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
    if journey.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return journey

@router.put("/{journey_id}", response_model=JourneyResponse)
def update_existing_journey(
    journey_id: int,
    journey_in: JourneyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    journey = get_journey(db, journey_id=journey_id)
    if not journey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
    if journey.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return update_journey(db, db_journey=journey, journey_in=journey_in)

@router.delete("/{journey_id}", response_model=JourneyResponse)
def delete_existing_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    journey = get_journey(db, journey_id=journey_id)
    if not journey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")
    if journey.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return delete_journey(db, db_journey=journey)
