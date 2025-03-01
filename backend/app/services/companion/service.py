"""Companion service implementation."""

import logging
from typing import Any, Dict, List, Optional

from app.database.session import get_db
from app.models.models import Companion, User
from app.schemas.companion import CompanionCreate, CompanionUpdate
from app.services.base.service import BaseService
from app.services.companion.interface import ICompanionService
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CompanionService(
    BaseService[Companion, CompanionCreate, CompanionUpdate], ICompanionService
):
    """Service for managing AI companions."""

    def __init__(self, db: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(model=Companion)
        self.db = db

    async def create_companion(
        self, user_id: int, companion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new AI companion.

        Args:
            user_id: ID of the user creating the companion
            companion_data: Data for creating the companion

        Returns:
            Dict with created companion data
        """
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create companion schema
            companion_in = CompanionCreate(**companion_data, user_id=user_id)

            # Create companion
            companion = await super().create(self.db, obj_in=companion_in)

            return {
                "status": "success",
                "data": {
                    "id": companion.id,
                    "name": companion.name,
                    "description": companion.description,
                    "created_at": companion.created_at,
                },
            }
        except Exception as e:
            logger.error(f"Error creating companion: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to create companion: {str(e)}"
            )

    async def get_companion(self, companion_id: int) -> Dict[str, Any]:
        """Get companion by ID.

        Args:
            companion_id: ID of the companion to retrieve

        Returns:
            Dict with companion data
        """
        try:
            companion = await super().get(self.db, id=companion_id)
            if not companion:
                raise HTTPException(status_code=404, detail="Companion not found")

            return {
                "status": "success",
                "data": {
                    "id": companion.id,
                    "name": companion.name,
                    "description": companion.description,
                    "personality": companion.personality,
                    "voice_id": companion.voice_id,
                    "live2d_model": companion.live2d_model,
                    "created_at": companion.created_at,
                    "updated_at": companion.updated_at,
                    "user_id": companion.user_id,
                },
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving companion: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve companion: {str(e)}"
            )

    async def list_companions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List companions for a user.

        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of companion data dictionaries
        """
        try:
            companions = await super().get_multi(
                self.db, skip=skip, limit=limit, filters={"user_id": user_id}
            )

            return [
                {
                    "id": companion.id,
                    "name": companion.name,
                    "description": companion.description,
                    "created_at": companion.created_at,
                }
                for companion in companions
            ]
        except Exception as e:
            logger.error(f"Error listing companions: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to list companions: {str(e)}"
            )

    async def update_companion(
        self, companion_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update companion settings.

        Args:
            companion_id: ID of the companion to update
            update_data: Data for updating the companion

        Returns:
            Dict with updated companion data
        """
        try:
            # Get existing companion
            companion = await super().get(self.db, id=companion_id)
            if not companion:
                raise HTTPException(status_code=404, detail="Companion not found")

            # Create update schema
            companion_in = CompanionUpdate(**update_data)

            # Update companion
            updated_companion = await super().update(
                self.db, db_obj=companion, obj_in=companion_in
            )

            return {
                "status": "success",
                "data": {
                    "id": updated_companion.id,
                    "name": updated_companion.name,
                    "description": updated_companion.description,
                    "updated_at": updated_companion.updated_at,
                },
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating companion: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to update companion: {str(e)}"
            )

    async def delete_companion(self, companion_id: int) -> Dict[str, Any]:
        """Delete a companion.

        Args:
            companion_id: ID of the companion to delete

        Returns:
            Dict with deletion status
        """
        try:
            # Delete companion
            companion = await super().delete(self.db, id=companion_id)

            return {
                "status": "success",
                "message": f"Companion '{companion.name}' deleted successfully",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting companion: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to delete companion: {str(e)}"
            )

    async def chat_with_companion(
        self,
        companion_id: int,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Chat with a companion.

        Args:
            companion_id: ID of the companion to chat with
            message: User message
            chat_history: Optional chat history

        Returns:
            Dict with companion response
        """
        try:
            # Get companion
            companion = await super().get(self.db, id=companion_id)
            if not companion:
                raise HTTPException(status_code=404, detail="Companion not found")

            # TODO: Implement actual chat logic with LLM integration
            # This is a placeholder implementation
            response = f"Hello! I am {companion.name}. This is a placeholder response."

            return {
                "status": "success",
                "data": {
                    "companion_id": companion_id,
                    "companion_name": companion.name,
                    "message": response,
                    "timestamp": "2023-01-01T00:00:00Z",  # Placeholder timestamp
                },
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error chatting with companion: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to chat with companion: {str(e)}"
            )


# Singleton instance
companion_service = CompanionService()
