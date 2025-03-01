"""Companion services package."""

from app.services.companion.interface import ICompanionService
from app.services.companion.service import CompanionService, companion_service

__all__ = [
    "ICompanionService",
    "CompanionService",
    "companion_service",
]
