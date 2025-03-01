"""Services package."""

# Base services
from app.services.base import IBaseService, BaseService

# Auth services
from app.services.auth import (
    TokenService,
    token_service,
    send_email,
    send_reset_password_email,
    send_verification_email,
)

# User services
from app.services.user import UserService

# Knowledge services
from app.services.knowledge import (
    KnowledgeService,
    KnowledgeBatchService,
    TagService,
    ConceptService,
    embeddings_service,
    IKnowledgeManager,
    KnowledgeManager,
)

# Permission services
from app.services.permissions import (
    PermissionService,
    get_permission_service,
)

# Companion services
from app.services.companion import (
    ICompanionService,
    CompanionService,
    companion_service,
)

# Live2D services
from app.services.live2d import (
    ILive2DService,
    Live2DService,
    live2d_service,
)

# TTS services
from app.services.tts import (
    ITTSService,
    TTSService,
    tts_service,
)

__all__ = [
    # Base
    "IBaseService",
    "BaseService",
    
    # Auth
    "TokenService",
    "token_service",
    "send_email",
    "send_reset_password_email",
    "send_verification_email",
    
    # User
    "UserService",
    
    # Knowledge
    "KnowledgeService",
    "KnowledgeBatchService",
    "TagService",
    "ConceptService",
    "embeddings_service",
    "IKnowledgeManager",
    "KnowledgeManager",
    
    # Permissions
    "PermissionService",
    "get_permission_service",
    
    # Companion
    "ICompanionService",
    "CompanionService",
    "companion_service",
    
    # Live2D
    "ILive2DService",
    "Live2DService",
    "live2d_service",
    
    # TTS
    "ITTSService",
    "TTSService",
    "tts_service",
] 