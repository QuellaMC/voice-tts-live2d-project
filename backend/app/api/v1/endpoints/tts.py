"""Text-to-speech endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_api_key
from app.database.session import get_db
from app.services.tts import tts_service

router = APIRouter()

@router.post("/synthesize")
async def synthesize_speech(
    text: str,
    voice_id: str,
    options: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Synthesize speech from text."""
    return await tts_service.synthesize(text=text, voice_id=voice_id, options=options)

@router.get("/voices")
async def list_voices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> List[dict]:
    """List available voices."""
    return await tts_service.list_voices()

@router.get("/voices/{voice_id}")
async def get_voice(
    voice_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Get voice details."""
    return await tts_service.get_voice(voice_id=voice_id)

@router.post("/voices")
async def create_voice(
    voice_name: str,
    samples: List[UploadFile] = File(...),
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Create a new custom voice."""
    sample_files = [sample.file for sample in samples]
    return await tts_service.create_voice(
        user_id=current_user["id"],
        voice_name=voice_name,
        samples=sample_files,
        description=description
    )

@router.delete("/voices/{voice_id}")
async def delete_voice(
    voice_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Delete a custom voice."""
    return await tts_service.delete_voice(voice_id=voice_id)

@router.get("/settings")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Get TTS settings for the current user."""
    return await tts_service.get_settings(user_id=current_user["id"])

@router.put("/settings")
async def update_settings(
    settings: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Update TTS settings for the current user."""
    return await tts_service.update_settings(
        user_id=current_user["id"],
        settings=settings
    ) 