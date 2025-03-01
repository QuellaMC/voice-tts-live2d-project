"""Base service class with common CRUD operations."""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from app.core.config import settings
from app.database.session import get_db
from fastapi import HTTPException
from pydantic import BaseModel
from redis import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for all services with common CRUD operations."""

    def __init__(
        self,
        model: Type[ModelType],
        redis_client: Optional[Redis] = None,
        cache_prefix: str = "",
        cache_ttl: int = settings.CACHE_TTL,
    ):
        """Initialize service with model and caching configuration."""
        self.model = model
        self.redis_client = redis_client
        self.cache_prefix = cache_prefix or model.__name__.lower()
        self.cache_ttl = cache_ttl

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key with prefix."""
        return f"{self.cache_prefix}:{key}"

    def _cache_get(self, key: str) -> Optional[Dict]:
        """Get item from cache."""
        if not self.redis_client:
            return None
        try:
            data = self.redis_client.get(self._get_cache_key(key))
            return data and json.loads(data)
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
            return None

    def _cache_set(self, key: str, value: Dict) -> None:
        """Set item in cache with TTL."""
        if not self.redis_client:
            return
        try:
            self.redis_client.setex(
                self._get_cache_key(key),
                timedelta(seconds=self.cache_ttl),
                json.dumps(value),
            )
        except Exception as e:
            logger.warning(f"Cache set error: {str(e)}")

    def _cache_delete(self, key: str) -> None:
        """Delete item from cache."""
        if not self.redis_client:
            return
        try:
            self.redis_client.delete(self._get_cache_key(key))
        except Exception as e:
            logger.warning(f"Cache delete error: {str(e)}")

    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            # Check cache first
            if cached := self._cache_get(str(id)):
                return self.model(**cached)

            # Get from database
            db_obj = db.query(self.model).filter(self.model.id == id).first()
            if db_obj:
                # Cache the result
                self._cache_set(str(id), db_obj.__dict__)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Database error in get: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        try:
            query = db.query(self.model)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_multi: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        try:
            obj_in_data = obj_in.dict()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            # Cache the new object
            self._cache_set(str(db_obj.id), db_obj.__dict__)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in create: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        try:
            obj_data = db_obj.__dict__
            update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            # Update cache
            self._cache_set(str(db_obj.id), db_obj.__dict__)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in update: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def delete(self, db: Session, *, id: Any) -> ModelType:
        """Delete a record by ID."""
        try:
            obj = db.query(self.model).get(id)
            if not obj:
                raise HTTPException(status_code=404, detail="Record not found")
            db.delete(obj)
            db.commit()
            # Remove from cache
            self._cache_delete(str(id))
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in delete: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

    async def count(self, db: Session, filters: Dict = None) -> int:
        """Count total records with optional filtering."""
        try:
            query = db.query(self.model)
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in count: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
