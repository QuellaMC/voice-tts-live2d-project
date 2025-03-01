"""Base service package."""

from app.services.base.interface import IBaseService
from app.services.base.service import BaseService

__all__ = [
    "IBaseService",
    "BaseService",
]
