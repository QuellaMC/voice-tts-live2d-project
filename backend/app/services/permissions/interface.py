"""Permissions service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session


class IPermissionService(ABC):
    """Interface for permission services."""

    @abstractmethod
    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        required_permission: str,
        resource_id: Optional[int] = None,
    ) -> bool:
        """Check if user has permission for a resource."""
        pass

    @abstractmethod
    async def add_user_to_group(
        self, user_id: int, group_id: int, added_by: int
    ) -> None:
        """Add user to a group."""
        pass

    @abstractmethod
    async def remove_user_from_group(self, user_id: int, group_id: int) -> None:
        """Remove user from a group."""
        pass

    @abstractmethod
    async def set_group_permission(
        self,
        group_id: int,
        resource_type: str,
        permissions: Dict[str, bool],
        resource_id: Optional[int] = None,
        created_by: int = None,
    ) -> None:
        """Set permissions for a group on a resource."""
        pass

    @abstractmethod
    async def log_access(
        self,
        user_id: int,
        knowledge_id: int,
        action: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log access to a resource."""
        pass
