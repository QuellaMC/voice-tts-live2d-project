"""Knowledge service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.models.knowledge import Knowledge
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from sqlalchemy.orm import Session


class IKnowledgeService(ABC):
    """Interface for knowledge services."""

    @abstractmethod
    async def create_with_relations(
        self,
        db: Session,
        *,
        obj_in: KnowledgeCreate,
        user_id: int,
        embedding: Optional[List[float]] = None
    ) -> Knowledge:
        """Create knowledge entry with tags and concepts."""
        pass

    @abstractmethod
    async def update_with_audit(
        self, db: Session, *, db_obj: Knowledge, obj_in: KnowledgeUpdate, user_id: int
    ) -> Knowledge:
        """Update knowledge entry with audit trail."""
        pass

    @abstractmethod
    async def search_similar(
        self,
        db: Session,
        *,
        query_embedding: List[float],
        limit: int = 5,
        min_similarity: float = 0.7,
        filter_tags: Optional[List[str]] = None,
        filter_concepts: Optional[List[str]] = None
    ) -> List[Knowledge]:
        """Search for similar knowledge entries using vector similarity."""
        pass

    @abstractmethod
    async def get_by_topic(self, db: Session, *, topic: str) -> Optional[Knowledge]:
        """Get knowledge entry by topic."""
        pass

    @abstractmethod
    async def get_by_tag(
        self, db: Session, *, tag_name: str, skip: int = 0, limit: int = 100
    ) -> List[Knowledge]:
        """Get knowledge entries by tag."""
        pass

    @abstractmethod
    async def get_by_concept(
        self, db: Session, *, concept_path: str, skip: int = 0, limit: int = 100
    ) -> List[Knowledge]:
        """Get knowledge entries by concept path."""
        pass

    @abstractmethod
    async def cleanup_old_entries(self, db: Session, *, days: int = 30) -> None:
        """Clean up knowledge entries not accessed in specified days."""
        pass


class IKnowledgeBatchService(ABC):
    """Interface for knowledge batch operations."""

    @abstractmethod
    async def create_many(
        self, db: Session, *, items: List[KnowledgeCreate], user_id: int
    ) -> List[Knowledge]:
        """Create multiple knowledge entries in batch."""
        pass

    @abstractmethod
    async def cleanup_orphaned(self, db: Session) -> Dict[str, int]:
        """Clean up orphaned tags and concepts."""
        pass

    @abstractmethod
    async def reindex_embeddings(
        self, db: Session, *, batch_size: int = 20
    ) -> Dict[str, int]:
        """Reindex embeddings for all knowledge entries."""
        pass
