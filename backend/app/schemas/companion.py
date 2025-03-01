"""Companion schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CompanionBase(BaseModel):
    """Base schema for companion data."""
    name: str
    description: Optional[str] = None
    personality: Optional[str] = None
    voice_id: Optional[str] = None
    live2d_model: Optional[str] = None


class CompanionCreate(CompanionBase):
    """Schema for creating a new companion."""
    user_id: int


class CompanionUpdate(CompanionBase):
    """Schema for updating a companion."""
    name: Optional[str] = None


class CompanionInDBBase(CompanionBase):
    """Base schema for companion in DB."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Companion(CompanionInDBBase):
    """Schema for companion response."""
    pass


class CompanionInDB(CompanionInDBBase):
    """Schema for companion in DB with additional fields."""
    pass 