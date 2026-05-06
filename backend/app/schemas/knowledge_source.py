from pydantic import BaseModel, ConfigDict
from typing import Optional

class KnowledgeSourceBase(BaseModel):
    title: str
    processing_status: Optional[str] = "pending"
    reference_id: Optional[str] = None
    user_id: Optional[int] = None

class KnowledgeSourceCreate(KnowledgeSourceBase):
    pass

class KnowledgeSourceUpdate(BaseModel):
    title: Optional[str] = None
    processing_status: Optional[str] = None
    reference_id: Optional[str] = None

class KnowledgeSourceResponse(KnowledgeSourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
