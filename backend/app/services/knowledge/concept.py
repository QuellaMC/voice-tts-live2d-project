"""Concept service implementation."""

import logging
from typing import Dict, List, Optional

from app.models.knowledge import Concept
from app.schemas.knowledge import ConceptCreate, ConceptUpdate
from app.services.base import BaseService
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConceptService(BaseService[Concept, ConceptCreate, ConceptUpdate]):
    """Service for managing concepts."""

    def __init__(self):
        """Initialize service with Concept model."""
        super().__init__(Concept)

    async def create_with_validation(
        self, db: Session, *, obj_in: ConceptCreate, user_id: int
    ) -> Concept:
        """Create concept with validation."""
        try:
            # Check if concept already exists
            existing = (
                db.query(Concept)
                .filter(
                    Concept.name == obj_in.name, Concept.parent_id == obj_in.parent_id
                )
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Concept '{obj_in.name}' already exists at this level",
                )

            # Validate parent if specified
            if obj_in.parent_id:
                parent = db.query(Concept).get(obj_in.parent_id)
                if not parent:
                    raise HTTPException(
                        status_code=404, detail="Parent concept not found"
                    )
                level = parent.level + 1
            else:
                level = 0

            # Create concept
            db_obj = Concept(
                name=obj_in.name,
                parent_id=obj_in.parent_id,
                level=level,
                description=obj_in.description,
                created_by=user_id,
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating concept: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create concept")

    async def update_with_validation(
        self, db: Session, *, db_obj: Concept, obj_in: ConceptUpdate, user_id: int
    ) -> Concept:
        """Update concept with validation."""
        try:
            # Check if new name already exists at same level
            if obj_in.name and obj_in.name != db_obj.name:
                existing = (
                    db.query(Concept)
                    .filter(
                        Concept.name == obj_in.name,
                        Concept.parent_id == (obj_in.parent_id or db_obj.parent_id),
                    )
                    .first()
                )
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Concept '{obj_in.name}' already exists at this level",
                    )

            # Validate new parent if specified
            if obj_in.parent_id and obj_in.parent_id != db_obj.parent_id:
                # Check for circular reference
                if await self._would_create_cycle(db, db_obj.id, obj_in.parent_id):
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot create circular reference in concept hierarchy",
                    )

                parent = db.query(Concept).get(obj_in.parent_id)
                if not parent:
                    raise HTTPException(
                        status_code=404, detail="Parent concept not found"
                    )
                obj_in.level = parent.level + 1

            # Update concept
            return await super().update(db, db_obj=db_obj, obj_in=obj_in)

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating concept: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update concept")

    async def _would_create_cycle(
        self, db: Session, concept_id: int, new_parent_id: int
    ) -> bool:
        """Check if setting new_parent_id as parent would create a cycle."""
        current = new_parent_id
        while current:
            if current == concept_id:
                return True
            parent = db.query(Concept).get(current)
            if not parent:
                break
            current = parent.parent_id
        return False

    async def get_by_path(self, db: Session, *, path: str) -> Optional[Concept]:
        """Get concept by path (e.g., 'parent/child/grandchild')."""
        parts = path.split("/")
        current_id = None

        for part in parts:
            concept = (
                db.query(Concept)
                .filter(Concept.name == part, Concept.parent_id == current_id)
                .first()
            )
            if not concept:
                return None
            current_id = concept.id

        return concept

    async def get_hierarchy(
        self, db: Session, *, root_id: Optional[int] = None
    ) -> List[Dict]:
        """Get concept hierarchy starting from optional root."""

        def build_tree(parent_id: Optional[int] = None) -> List[Dict]:
            concepts = db.query(Concept).filter(Concept.parent_id == parent_id).all()

            return [
                {
                    "id": concept.id,
                    "name": concept.name,
                    "description": concept.description,
                    "level": concept.level,
                    "children": build_tree(concept.id),
                }
                for concept in concepts
            ]

        return build_tree(root_id)

    async def get_ancestors(self, db: Session, *, concept_id: int) -> List[Concept]:
        """Get all ancestors of a concept."""
        ancestors = []
        current = db.query(Concept).get(concept_id)

        while current and current.parent_id:
            parent = db.query(Concept).get(current.parent_id)
            if parent:
                ancestors.append(parent)
            current = parent

        return ancestors

    async def get_descendants(self, db: Session, *, concept_id: int) -> List[Concept]:
        """Get all descendants of a concept."""
        descendants = []
        queue = [concept_id]

        while queue:
            current_id = queue.pop(0)
            children = db.query(Concept).filter(Concept.parent_id == current_id).all()

            for child in children:
                descendants.append(child)
                queue.append(child.id)

        return descendants
