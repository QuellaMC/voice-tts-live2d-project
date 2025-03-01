"""Knowledge batch operations service."""

import asyncio
import logging
from typing import Any, Dict, List

import openai
from app.core.config import settings
from app.models.knowledge import (
    Concept,
    Knowledge,
    Tag,
    knowledge_concepts,
    knowledge_tags,
)
from app.schemas.knowledge import KnowledgeCreate
from app.services.knowledge.interface import IKnowledgeBatchService
from app.services.knowledge.service import KnowledgeService
from fastapi import HTTPException
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class KnowledgeBatchService(IKnowledgeBatchService):
    """Service for batch operations on knowledge base."""

    def __init__(self):
        """Initialize service."""
        self.knowledge_service = KnowledgeService()
        openai.api_key = settings.OPENAI_API_KEY

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 20
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        if not texts:
            return []

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = await openai.Embedding.acreate(
                    input=batch, model="text-embedding-3-small"
                )
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)

                # Sleep briefly to respect rate limits
                await asyncio.sleep(0.1)

            except openai.error.RateLimitError:
                logger.warning(
                    "OpenAI rate limit hit, retrying after exponential backoff"
                )
                raise
            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                all_embeddings.extend([[] for _ in batch])

        return all_embeddings

    async def create_many(
        self, db: Session, *, items: List[KnowledgeCreate], user_id: int
    ) -> List[Knowledge]:
        """Create multiple knowledge entries in batch."""
        if not items:
            return []

        try:
            # Generate embeddings for all items
            texts = [item.content for item in items]
            embeddings = await self._generate_embeddings_batch(texts)

            # Create knowledge entries
            created_items = []
            for item, embedding in zip(items, embeddings):
                try:
                    knowledge = await self.knowledge_service.create_with_relations(
                        db, obj_in=item, user_id=user_id, embedding=embedding
                    )
                    created_items.append(knowledge)
                except Exception as e:
                    logger.error(f"Error creating knowledge entry: {str(e)}")
                    continue

            return created_items

        except Exception as e:
            db.rollback()
            logger.error(f"Error in batch creation: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create knowledge entries in batch"
            )

    async def cleanup_orphaned(self, db: Session) -> Dict[str, int]:
        """Clean up orphaned tags and concepts."""
        try:
            # Find orphaned tags
            orphaned_tags = (
                db.query(Tag)
                .outerjoin(knowledge_tags)
                .filter(knowledge_tags.c.tag_id.is_(None))
                .all()
            )

            # Find orphaned concepts
            orphaned_concepts = (
                db.query(Concept)
                .outerjoin(knowledge_concepts)
                .filter(knowledge_concepts.c.concept_id.is_(None))
                .filter(Concept.children.any() == False)
                .all()
            )

            # Delete orphaned items
            for tag in orphaned_tags:
                db.delete(tag)

            for concept in orphaned_concepts:
                db.delete(concept)

            db.commit()

            return {
                "tags_removed": len(orphaned_tags),
                "concepts_removed": len(orphaned_concepts),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up orphaned items: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to clean up orphaned items"
            )

    async def reindex_embeddings(
        self, db: Session, *, batch_size: int = 20
    ) -> Dict[str, int]:
        """Reindex embeddings for all knowledge entries."""
        try:
            # Get all entries without embeddings
            entries = db.query(Knowledge).filter(Knowledge.embedding.is_(None)).all()

            if not entries:
                return {"reindexed": 0}

            # Generate embeddings in batches
            texts = [entry.content for entry in entries]
            embeddings = await self._generate_embeddings_batch(
                texts, batch_size=batch_size
            )

            # Update entries with new embeddings
            updated = 0
            for entry, embedding in zip(entries, embeddings):
                if embedding:
                    entry.embedding = embedding
                    updated += 1

            db.commit()
            return {"reindexed": updated}

        except Exception as e:
            db.rollback()
            logger.error(f"Error reindexing embeddings: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to reindex embeddings")
