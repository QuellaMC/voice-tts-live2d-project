"""Knowledge service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import openai
from app.core.config import settings
from app.models.knowledge import (
    Concept,
    Knowledge,
    KnowledgeAudit,
    Tag,
    knowledge_concepts,
    knowledge_tags,
)
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from app.services.base import BaseService
from app.services.knowledge.concept import ConceptService
from app.services.knowledge.interface import IKnowledgeService
from app.services.knowledge.tag import TagService
from fastapi import HTTPException
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class KnowledgeService(
    BaseService[Knowledge, KnowledgeCreate, KnowledgeUpdate], IKnowledgeService
):
    """Service for managing knowledge base."""

    def __init__(self):
        """Initialize service with Knowledge model."""
        super().__init__(
            Knowledge, cache_prefix="knowledge", cache_ttl=settings.CACHE_TTL
        )
        self.tag_service = TagService()
        self.concept_service = ConceptService()
        openai.api_key = settings.OPENAI_API_KEY

    async def create_with_relations(
        self,
        db: Session,
        *,
        obj_in: KnowledgeCreate,
        user_id: int,
        embedding: Optional[List[float]] = None,
    ) -> Knowledge:
        """Create knowledge entry with tags and concepts."""
        try:
            # Generate embedding if not provided
            if embedding is None:
                embedding = await self._generate_embedding(obj_in.content)

            # Create knowledge entry
            db_obj = Knowledge(
                topic=obj_in.topic,
                content=obj_in.content,
                question=obj_in.question,
                answer=obj_in.answer,
                metadata=obj_in.metadata,
                embedding=embedding,
                created_by=str(user_id),
            )

            # Add tags
            if obj_in.tags:
                for tag_name in obj_in.tags:
                    tag = await self.tag_service.get_or_create(
                        db, name=tag_name, user_id=user_id
                    )
                    db_obj.tags.append(tag)

            # Add concepts
            if obj_in.concepts:
                for concept_path in obj_in.concepts:
                    concept = await self.concept_service.get_by_path(
                        db, path=concept_path
                    )
                    if not concept:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Concept path '{concept_path}' not found",
                        )
                    db_obj.concepts.append(concept)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            # Create audit entry
            audit = KnowledgeAudit(
                knowledge_id=db_obj.id,
                user_id=user_id,
                action="create",
                details={"original": obj_in.dict()},
            )
            db.add(audit)
            db.commit()

            # Cache the new object
            self._cache_set(str(db_obj.id), db_obj.__dict__)

            return db_obj

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating knowledge entry: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create knowledge entry"
            )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API with caching."""
        try:
            # Check cache first
            cache_key = f"embedding:{hash(text)}"
            if cached := self._cache_get(cache_key):
                return cached

            # Generate new embedding
            response = await openai.Embedding.acreate(
                input=text, model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding

            # Cache the result
            self._cache_set(cache_key, embedding)

            return embedding
        except openai.error.RateLimitError:
            logger.warning("OpenAI rate limit hit, retrying after exponential backoff")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []

    async def search_similar(
        self,
        db: Session,
        *,
        query_embedding: List[float],
        limit: int = 5,
        min_similarity: float = 0.7,
        filter_tags: Optional[List[str]] = None,
        filter_concepts: Optional[List[str]] = None,
    ) -> List[Knowledge]:
        """Search for similar knowledge entries using vector similarity."""
        try:
            # Convert query embedding to numpy array
            query_vector = np.array(query_embedding)

            # Build query
            query = db.query(Knowledge).filter(Knowledge.embedding.isnot(None))

            # Apply filters
            if filter_tags:
                query = query.join(Knowledge.tags).filter(Tag.name.in_(filter_tags))
            if filter_concepts:
                query = query.join(Knowledge.concepts).filter(
                    Concept.name.in_(filter_concepts)
                )

            # Get entries
            entries = query.all()

            # Calculate similarities
            similarities = []
            for entry in entries:
                similarity = self._calculate_similarity(
                    query_vector, np.array(entry.embedding)
                )
                if similarity >= min_similarity:
                    similarities.append((entry, similarity))

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = [entry for entry, _ in similarities[:limit]]

            # Update last accessed timestamp
            for entry in results:
                entry.last_accessed_at = datetime.utcnow()
            db.commit()

            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to perform similarity search"
            )

    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def update_with_audit(
        self, db: Session, *, db_obj: Knowledge, obj_in: KnowledgeUpdate, user_id: int
    ) -> Knowledge:
        """Update knowledge entry with audit trail."""
        try:
            # Store original state for audit
            original_state = {
                "topic": db_obj.topic,
                "content": db_obj.content,
                "question": db_obj.question,
                "answer": db_obj.answer,
                "metadata": db_obj.metadata,
                "tags": [tag.name for tag in db_obj.tags],
                "concepts": [concept.name for concept in db_obj.concepts],
            }

            # Generate new embedding if content changed
            if obj_in.content:
                obj_in.embedding = await self._generate_embedding(obj_in.content)

            # Update tags if provided
            if obj_in.tags is not None:
                db_obj.tags = []
                for tag_name in obj_in.tags:
                    tag = await self.tag_service.get_or_create(
                        db, name=tag_name, user_id=user_id
                    )
                    db_obj.tags.append(tag)

            # Update concepts if provided
            if obj_in.concepts is not None:
                db_obj.concepts = []
                for concept_path in obj_in.concepts:
                    concept = await self.concept_service.get_by_path(
                        db, path=concept_path
                    )
                    if not concept:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Concept path '{concept_path}' not found",
                        )
                    db_obj.concepts.append(concept)

            # Update knowledge entry
            updated_obj = await super().update(db, db_obj=db_obj, obj_in=obj_in)

            # Create audit entry
            audit = KnowledgeAudit(
                knowledge_id=updated_obj.id,
                user_id=user_id,
                action="update",
                details={
                    "original": original_state,
                    "changes": obj_in.dict(exclude_unset=True),
                },
            )
            db.add(audit)
            db.commit()

            # Update cache
            self._cache_set(str(updated_obj.id), updated_obj.__dict__)

            return updated_obj

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating knowledge entry: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to update knowledge entry"
            )

    async def get_by_topic(self, db: Session, *, topic: str) -> Optional[Knowledge]:
        """Get knowledge entry by topic."""
        return db.query(Knowledge).filter(Knowledge.topic == topic).first()

    async def get_by_tag(
        self, db: Session, *, tag_name: str, skip: int = 0, limit: int = 100
    ) -> List[Knowledge]:
        """Get knowledge entries by tag."""
        return (
            db.query(Knowledge)
            .join(Knowledge.tags)
            .filter(Tag.name == tag_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_by_concept(
        self, db: Session, *, concept_path: str, skip: int = 0, limit: int = 100
    ) -> List[Knowledge]:
        """Get knowledge entries by concept path."""
        concept = await self.concept_service.get_by_path(db, path=concept_path)
        if not concept:
            return []

        return (
            db.query(Knowledge)
            .join(Knowledge.concepts)
            .filter(Concept.id == concept.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def cleanup_old_entries(self, db: Session, *, days: int = 30) -> None:
        """Clean up knowledge entries not accessed in specified days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            old_entries = (
                db.query(Knowledge).filter(Knowledge.last_accessed_at < cutoff).all()
            )

            for entry in old_entries:
                # Remove from cache
                self._cache_delete(str(entry.id))
                # Create audit entry
                audit = KnowledgeAudit(
                    knowledge_id=entry.id,
                    user_id=None,
                    action="cleanup",
                    details={"reason": "not accessed"},
                )
                db.add(audit)

            db.commit()
            logger.info(f"Cleaned up {len(old_entries)} old knowledge entries")

        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up old entries: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to clean up old entries"
            )
