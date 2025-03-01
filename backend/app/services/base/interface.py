"""Base service interface."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class IBaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Interface for base service with common CRUD operations."""
    
    @abstractmethod
    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        pass
        
    @abstractmethod
    async def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        pass
        
    @abstractmethod
    async def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record."""
        pass
        
    @abstractmethod
    async def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        pass
        
    @abstractmethod
    async def delete(self, db: Session, *, id: Any) -> ModelType:
        """Delete a record by ID."""
        pass
        
    @abstractmethod
    async def count(self, db: Session, filters: Dict = None) -> int:
        """Count total records with optional filtering."""
        pass 