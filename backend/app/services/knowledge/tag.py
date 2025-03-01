"""Tag service implementation."""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.knowledge import Tag
from app.schemas.knowledge import TagCreate, TagUpdate
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class TagService(BaseService[Tag, TagCreate, TagUpdate]):
    """Service for managing tags."""

    def __init__(self):
        """Initialize service with Tag model."""
        super().__init__(Tag)

    async def create_with_validation(
        self,
        db: Session,
        *,
        obj_in: TagCreate,
        user_id: int
    ) -> Tag:
        """Create tag with validation."""
        try:
            # Check if tag already exists
            existing = db.query(Tag).filter(Tag.name == obj_in.name).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tag '{obj_in.name}' already exists"
                )

            # Create tag
            db_obj = Tag(
                name=obj_in.name,
                description=obj_in.description,
                created_by=user_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating tag: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create tag"
            )

    async def update_with_validation(
        self,
        db: Session,
        *,
        db_obj: Tag,
        obj_in: TagUpdate,
        user_id: int
    ) -> Tag:
        """Update tag with validation."""
        try:
            # Check if new name already exists
            if obj_in.name and obj_in.name != db_obj.name:
                existing = db.query(Tag).filter(Tag.name == obj_in.name).first()
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Tag '{obj_in.name}' already exists"
                    )

            # Update tag
            return await super().update(db, db_obj=db_obj, obj_in=obj_in)

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating tag: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update tag"
            )

    async def get_by_name(
        self,
        db: Session,
        *,
        name: str
    ) -> Optional[Tag]:
        """Get tag by name."""
        return db.query(Tag).filter(Tag.name == name).first()

    async def get_multiple_by_names(
        self,
        db: Session,
        *,
        names: List[str]
    ) -> List[Tag]:
        """Get multiple tags by names."""
        return db.query(Tag).filter(Tag.name.in_(names)).all()

    async def get_or_create(
        self,
        db: Session,
        *,
        name: str,
        description: Optional[str] = None,
        user_id: int
    ) -> Tag:
        """Get existing tag or create new one."""
        tag = await self.get_by_name(db, name=name)
        if not tag:
            tag = await self.create_with_validation(
                db,
                obj_in=TagCreate(name=name, description=description),
                user_id=user_id
            )
        return tag 