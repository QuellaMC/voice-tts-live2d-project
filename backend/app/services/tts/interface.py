"""Text-to-Speech service interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, BinaryIO


class ITTSService(ABC):
    """Interface for Text-to-Speech operations."""
    
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize speech from text."""
        pass
        
    @abstractmethod
    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices."""
        pass
        
    @abstractmethod
    async def get_voice(self, voice_id: str) -> Dict[str, Any]:
        """Get voice details."""
        pass
        
    @abstractmethod
    async def create_voice(self, user_id: int, voice_name: str, samples: List[BinaryIO], description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new custom voice."""
        pass
        
    @abstractmethod
    async def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        """Delete a custom voice."""
        pass
        
    @abstractmethod
    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Get TTS settings for a user."""
        pass
        
    @abstractmethod
    async def update_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update TTS settings for a user."""
        pass 