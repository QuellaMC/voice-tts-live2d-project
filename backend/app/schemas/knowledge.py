"""Knowledge schema models."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class KnowledgeBase(BaseModel):
    """Base knowledge schema."""
    topic: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    question: Optional[str] = None
    answer: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []
    concepts: Optional[List[str]] = []

class KnowledgeCreate(KnowledgeBase):
    """Schema for creating knowledge entry."""
    pass

class KnowledgeUpdate(BaseModel):
    """Schema for updating knowledge entry."""
    topic: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    question: Optional[str] = None
    answer: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    concepts: Optional[List[str]] = None

class TagBase(BaseModel):
    """Base tag schema."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class TagCreate(TagBase):
    """Schema for creating tag."""
    pass

class TagUpdate(TagBase):
    """Schema for updating tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None

class ConceptBase(BaseModel):
    """Base concept schema."""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    level: int = 0
    description: Optional[str] = None

class ConceptCreate(ConceptBase):
    """Schema for creating concept."""
    pass

class ConceptUpdate(ConceptBase):
    """Schema for updating concept."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = None
    level: Optional[int] = None
    description: Optional[str] = None

class KnowledgeInDB(KnowledgeBase):
    """Schema for knowledge in database."""
    id: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    embedding: Optional[List[float]] = None

    class Config:
        orm_mode = True

class TagInDB(TagBase):
    """Schema for tag in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ConceptInDB(ConceptBase):
    """Schema for concept in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class KnowledgeResponse(KnowledgeInDB):
    """Schema for knowledge response."""
    tags: List[TagInDB] = []
    concepts: List[ConceptInDB] = []

class KnowledgeList(BaseModel):
    """Schema for paginated knowledge list."""
    items: List[KnowledgeResponse]
    total: int
    skip: int
    limit: int

    class Config:
        orm_mode = True 