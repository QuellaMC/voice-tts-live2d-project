"""Live2D integration endpoints."""

from typing import List, Optional

from app.core.security import get_api_key, get_current_user
from app.database.session import get_db
from app.services.live2d import live2d_service
from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/animate")
async def animate_model(
    model_id: str,
    motion_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Animate Live2D model with motion data."""
    return await live2d_service.animate(model_id=model_id, motion_data=motion_data)


@router.get("/models")
async def list_models(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> List[dict]:
    """List available Live2D models."""
    return await live2d_service.list_models()


@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Get Live2D model details."""
    return await live2d_service.get_model(model_id=model_id)


@router.post("/models")
async def upload_model(
    model_name: str,
    model_file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Upload a new Live2D model."""
    return await live2d_service.upload_model(
        user_id=current_user["id"],
        model_name=model_name,
        model_file=model_file.file,
        thumbnail=thumbnail.file if thumbnail else None,
    )


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Delete a Live2D model."""
    return await live2d_service.delete_model(model_id=model_id)


@router.get("/settings")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Get Live2D settings for the current user."""
    return await live2d_service.get_settings(user_id=current_user["id"])


@router.put("/settings")
async def update_settings(
    settings: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> dict:
    """Update Live2D settings for the current user."""
    return await live2d_service.update_settings(
        user_id=current_user["id"], settings=settings
    )
