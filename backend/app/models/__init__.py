"""Models package."""

from app.models.api_key import APIKey
from app.models.base import Base
from app.models.group_permission import GroupPermission
from app.models.knowledge import (
    Concept,
    Knowledge,
    KnowledgeAudit,
    Tag,
    knowledge_concepts,
    knowledge_tags,
)
from app.models.models import (
    AdminApiKey,
    ApiProvider,
    Companion,
    Conversation,
    Message,
    Space,
)
from app.models.models import User as MainUser
from app.models.models import (
    UserApiKey,
    UserRole,
)
from app.models.user import User
from app.models.user_group import UserGroup, user_group_members

__all__ = [
    "Base",
    "User",
    "APIKey",
    "UserGroup",
    "user_group_members",
    "GroupPermission",
    "Knowledge",
    "Tag",
    "Concept",
    "KnowledgeAudit",
    "knowledge_tags",
    "knowledge_concepts",
    # From models.py
    "UserRole",
    "MainUser",
    "ApiProvider",
    "AdminApiKey",
    "UserApiKey",
    "Space",
    "Conversation",
    "Message",
    "Companion",
]
