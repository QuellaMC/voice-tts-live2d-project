"""API router configuration."""

from app.api.v1.endpoints import (
    auth,
    companion,
    groups,
    knowledge,
    live2d,
    root,
    tts,
    users,
)
from fastapi import APIRouter

api_router = APIRouter()

# Include all routers
api_router.include_router(root.router, tags=["Root"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(tts.router, prefix="/tts", tags=["Text-to-Speech"])
api_router.include_router(live2d.router, prefix="/live2d", tags=["Live2D"])
api_router.include_router(companion.router, prefix="/companion", tags=["AI Companion"])
api_router.include_router(
    knowledge.router, prefix="/knowledge", tags=["Knowledge Base"]
)
