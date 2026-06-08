from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteUpdate

def get_favorite(db: Session, favorite_id: int) -> Optional[Favorite]:
    return db.execute(select(Favorite).where(Favorite.id == favorite_id)).scalar_one_or_none()

def get_favorites_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Favorite]:
    return list(db.execute(select(Favorite).where(Favorite.user_id == user_id).offset(skip).limit(limit)).scalars().all())

def create_favorite(db: Session, favorite: FavoriteCreate, user_id: int) -> Favorite:
    db_favorite = Favorite(**favorite.model_dump(), user_id=user_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def update_favorite(db: Session, db_favorite: Favorite, favorite_in: FavoriteUpdate) -> Favorite:
    update_data = favorite_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_favorite, field, value)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def delete_favorite(db: Session, db_favorite: Favorite) -> Favorite:
    db.delete(db_favorite)
    db.commit()
    return db_favorite
