"""API response models."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")

class ResponseBase(GenericModel, Generic[DataT]):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[DataT] = None

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str 