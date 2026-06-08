from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.crud.crud_favorite import get_favorite, get_favorites_by_user, create_favorite, delete_favorite
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    *,
    db: Session = Depends(get_db),
    favorite_in: FavoriteCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Save a new item to the user's favorites.
    """
    return create_favorite(db, favorite=favorite_in, user_id=current_user.id)

@router.get("/", response_model=List[FavoriteResponse])
def read_favorites(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all favorites for the current logged-in user.
    """
    return get_favorites_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.delete("/{favorite_id}", response_model=FavoriteResponse)
def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a favorite by its ID.
    """
    favorite = get_favorite(db, favorite_id=favorite_id)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    if favorite.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return delete_favorite(db, db_favorite=favorite)
