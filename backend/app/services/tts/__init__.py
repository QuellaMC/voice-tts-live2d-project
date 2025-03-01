"""Text-to-Speech services package."""

from app.services.tts.interface import ITTSService
from app.services.tts.service import TTSService, tts_service

__all__ = [
    "ITTSService",
    "TTSService",
    "tts_service",
] 