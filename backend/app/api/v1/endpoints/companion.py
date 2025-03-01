"""AI companion endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_api_key
from app.database.session import get_db
from app.services.companion import companion_service

router = APIRouter()

@router.post("/chat")
async def chat_with_companion(
    message: str,
    companion_id: int,
    chat_history: Optional[List[dict]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Chat with AI companion."""
    return await companion_service.chat_with_companion(
        companion_id=companion_id,
        message=message,
        chat_history=chat_history
    )

@router.get("/companions")
async def list_companions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> List[dict]:
    """List available AI companions."""
    return await companion_service.list_companions(
        user_id=current_user["id"],
        skip=skip,
        limit=limit
    )

@router.post("/companions")
async def create_companion(
    companion_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Create a new AI companion."""
    return await companion_service.create_companion(
        user_id=current_user["id"],
        companion_data=companion_data
    )

@router.get("/companions/{companion_id}")
async def get_companion(
    companion_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Get companion details."""
    return await companion_service.get_companion(companion_id=companion_id)

@router.put("/companions/{companion_id}")
async def update_companion(
    companion_id: int,
    update_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Update companion settings."""
    return await companion_service.update_companion(
        companion_id=companion_id,
        update_data=update_data
    )

@router.delete("/companions/{companion_id}")
async def delete_companion(
    companion_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Delete a companion."""
    return await companion_service.delete_companion(companion_id=companion_id) 