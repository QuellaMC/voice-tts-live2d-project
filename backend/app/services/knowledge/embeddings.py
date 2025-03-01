"""Embeddings service implementation."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import openai
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service for generating and managing embeddings."""

    def __init__(self):
        """Initialize embeddings service."""
        self.model = "text-embedding-3-small"
        self.cache = {}
        openai.api_key = settings.OPENAI_API_KEY

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API."""
        try:
            # Check cache first
            cache_key = hash(text)
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Generate new embedding
            response = await openai.Embedding.acreate(input=text, model=self.model)
            embedding = response.data[0].embedding

            # Cache the result
            self.cache[cache_key] = embedding

            return embedding
        except openai.error.RateLimitError:
            logger.warning("OpenAI rate limit hit, retrying after exponential backoff")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 20
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        if not texts:
            return []

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                # Check cache first
                cached_embeddings = []
                texts_to_embed = []
                indices = []

                for j, text in enumerate(batch):
                    cache_key = hash(text)
                    if cache_key in self.cache:
                        cached_embeddings.append((j, self.cache[cache_key]))
                    else:
                        texts_to_embed.append(text)
                        indices.append(j)

                # Generate new embeddings
                if texts_to_embed:
                    response = await openai.Embedding.acreate(
                        input=texts_to_embed, model=self.model
                    )

                    # Cache the results
                    for idx, item in zip(indices, response.data):
                        embedding = item.embedding
                        self.cache[hash(batch[idx])] = embedding
                        cached_embeddings.append((idx, embedding))

                # Sort by original index
                cached_embeddings.sort(key=lambda x: x[0])
                all_embeddings.extend([emb for _, emb in cached_embeddings])

            except openai.error.RateLimitError:
                logger.warning(
                    "OpenAI rate limit hit, retrying after exponential backoff"
                )
                raise
            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                all_embeddings.extend([[] for _ in batch])

        return all_embeddings

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        np_vec1 = np.array(vec1)
        np_vec2 = np.array(vec2)

        return float(
            np.dot(np_vec1, np_vec2)
            / (np.linalg.norm(np_vec1) * np.linalg.norm(np_vec2))
        )

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.cache.clear()

    def get_cache_size(self) -> int:
        """Get the current size of the embedding cache."""
        return len(self.cache)


embeddings_service = EmbeddingsService()
