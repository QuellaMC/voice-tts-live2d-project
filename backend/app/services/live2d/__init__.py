"""Live2D services package."""

from app.services.live2d.interface import ILive2DService
from app.services.live2d.service import Live2DService, live2d_service

__all__ = [
    "ILive2DService",
    "Live2DService",
    "live2d_service",
]
