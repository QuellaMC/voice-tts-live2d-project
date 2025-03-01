"""Live2D service interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, BinaryIO


class ILive2DService(ABC):
    """Interface for Live2D operations."""
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Live2D models."""
        pass
        
    @abstractmethod
    async def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get Live2D model details."""
        pass
        
    @abstractmethod
    async def upload_model(self, user_id: int, model_name: str, model_file: BinaryIO, thumbnail: Optional[BinaryIO] = None) -> Dict[str, Any]:
        """Upload a new Live2D model."""
        pass
        
    @abstractmethod
    async def delete_model(self, model_id: str) -> Dict[str, Any]:
        """Delete a Live2D model."""
        pass
        
    @abstractmethod
    async def animate(self, model_id: str, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Animate a Live2D model with motion data."""
        pass
        
    @abstractmethod
    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Get Live2D settings for a user."""
        pass
        
    @abstractmethod
    async def update_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update Live2D settings for a user."""
        pass 