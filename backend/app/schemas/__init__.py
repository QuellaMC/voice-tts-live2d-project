"""Schemas package."""

from app.schemas.companion import (
    Companion,
    CompanionBase,
    CompanionCreate,
    CompanionInDB,
    CompanionInDBBase,
    CompanionUpdate,
)
from app.schemas.knowledge import (
    ConceptBase,
    ConceptCreate,
    ConceptInDB,
    ConceptUpdate,
    KnowledgeBase,
    KnowledgeCreate,
    KnowledgeInDB,
    KnowledgeList,
    KnowledgeResponse,
    KnowledgeUpdate,
    TagBase,
    TagCreate,
    TagInDB,
    TagUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserInDB,
    UserList,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserList",
    # Knowledge schemas
    "KnowledgeBase",
    "KnowledgeCreate",
    "KnowledgeUpdate",
    "KnowledgeInDB",
    "KnowledgeResponse",
    "KnowledgeList",
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagInDB",
    "ConceptBase",
    "ConceptCreate",
    "ConceptUpdate",
    "ConceptInDB",
    # Companion schemas
    "CompanionBase",
    "CompanionCreate",
    "CompanionUpdate",
    "CompanionInDBBase",
    "Companion",
    "CompanionInDB",
]
