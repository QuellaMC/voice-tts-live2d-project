from fastapi import APIRouter
from app.schemas.response import ResponseBase

router = APIRouter()

@router.get('/', response_model=ResponseBase)
async def root():
    return {"success": True, "message": "Welcome to the AI Anime Companion API"}

@router.get('/health', response_model=ResponseBase)
async def health_check():
    return {"success": True, "message": "Service is healthy", "data": {"status": "healthy", "version": "0.1.0"}} 