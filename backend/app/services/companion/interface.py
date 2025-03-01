"""Companion service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ICompanionService(ABC):
    """Interface for AI companion operations."""

    @abstractmethod
    async def create_companion(
        self, user_id: int, companion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new AI companion."""
        pass

    @abstractmethod
    async def get_companion(self, companion_id: int) -> Dict[str, Any]:
        """Get companion by ID."""
        pass

    @abstractmethod
    async def list_companions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List companions for a user."""
        pass

    @abstractmethod
    async def update_companion(
        self, companion_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update companion settings."""
        pass

    @abstractmethod
    async def delete_companion(self, companion_id: int) -> Dict[str, Any]:
        """Delete a companion."""
        pass

    @abstractmethod
    async def chat_with_companion(
        self,
        companion_id: int,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Chat with a companion."""
        pass
