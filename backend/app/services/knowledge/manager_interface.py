"""Knowledge manager interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class IKnowledgeManager(ABC):
    """Interface for knowledge management operations."""
    
    @abstractmethod
    def upload_knowledge(self, topic: str, content: str, tags: Optional[List[str]] = None) -> Dict:
        """Store new knowledge entry."""
        pass

    @abstractmethod
    def retrieve_knowledge(self, query: str) -> Dict:
        """Retrieve knowledge based on query."""
        pass

    @abstractmethod
    def list_topics(self) -> List[Dict]:
        """List all available knowledge topics."""
        pass

    @abstractmethod
    def update_knowledge(self, topic: str, new_content: str, tags: Optional[List[str]] = None) -> Dict:
        """Update existing knowledge entry."""
        pass

    @abstractmethod
    def delete_knowledge(self, topic: str) -> Dict:
        """Delete knowledge entry."""
        pass 