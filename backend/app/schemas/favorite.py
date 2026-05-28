from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class FavoriteBase(BaseModel):
    item_type: str
    item_content: str

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteUpdate(BaseModel):
    item_type: Optional[str] = None
    item_content: Optional[str] = None

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
