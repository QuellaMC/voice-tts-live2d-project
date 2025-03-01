"""Permissions service implementation."""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends

from app.database.session import get_db
from app.models.user_group import UserGroup, user_group_members
from app.models.group_permission import GroupPermission
from app.models.knowledge import KnowledgeAudit
from app.services.permissions.interface import IPermissionService

logger = logging.getLogger(__name__)

class PermissionService(IPermissionService):
    """Service for managing permissions."""

    def __init__(self, db: Session = None):
        """Initialize permission service."""
        self.db = db

    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        required_permission: str,
        resource_id: Optional[int] = None
    ) -> bool:
        """Check if user has permission for a resource."""
        try:
            # Get user's groups
            user_groups = self.db.query(UserGroup).join(
                user_group_members
            ).filter(
                user_group_members.c.user_id == user_id
            ).all()
            
            group_ids = [group.id for group in user_groups]
            
            if not group_ids:
                return False
            
            # Check permissions for each group
            query = self.db.query(GroupPermission).filter(
                GroupPermission.group_id.in_(group_ids),
                GroupPermission.resource_type == resource_type
            )
            
            if resource_id:
                # Check for specific resource or global permission
                query = query.filter(
                    (GroupPermission.resource_id == resource_id) | 
                    (GroupPermission.resource_id.is_(None))
                )
            else:
                # Check for global permission only
                query = query.filter(GroupPermission.resource_id.is_(None))
            
            permissions = query.all()
            
            # Check if any permission grants the required access
            for permission in permissions:
                if required_permission == "read" and permission.can_read:
                    return True
                if required_permission == "write" and permission.can_write:
                    return True
                if required_permission == "delete" and permission.can_delete:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    async def add_user_to_group(
        self,
        user_id: int,
        group_id: int,
        added_by: int
    ) -> None:
        """Add user to a group."""
        try:
            # Check if user is already in the group
            existing = self.db.query(user_group_members).filter(
                user_group_members.c.user_id == user_id,
                user_group_members.c.group_id == group_id
            ).first()
            
            if existing:
                return
            
            # Add user to group
            stmt = user_group_members.insert().values(
                user_id=user_id,
                group_id=group_id,
                added_by=added_by,
                added_at=datetime.utcnow()
            )
            
            self.db.execute(stmt)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding user to group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to add user to group"
            )

    async def remove_user_from_group(
        self,
        user_id: int,
        group_id: int
    ) -> None:
        """Remove user from a group."""
        try:
            # Remove user from group
            stmt = user_group_members.delete().where(
                user_group_members.c.user_id == user_id,
                user_group_members.c.group_id == group_id
            )
            
            self.db.execute(stmt)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing user from group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to remove user from group"
            )

    async def set_group_permission(
        self,
        group_id: int,
        resource_type: str,
        permissions: Dict[str, bool],
        resource_id: Optional[int] = None,
        created_by: int = None
    ) -> None:
        """Set permissions for a group on a resource."""
        try:
            # Check if permission already exists
            existing = self.db.query(GroupPermission).filter(
                GroupPermission.group_id == group_id,
                GroupPermission.resource_type == resource_type,
                GroupPermission.resource_id == resource_id
            ).first()
            
            if existing:
                # Update existing permission
                existing.can_read = permissions.get("can_read", existing.can_read)
                existing.can_write = permissions.get("can_write", existing.can_write)
                existing.can_delete = permissions.get("can_delete", existing.can_delete)
                self.db.add(existing)
            else:
                # Create new permission
                permission = GroupPermission(
                    group_id=group_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    can_read=permissions.get("can_read", False),
                    can_write=permissions.get("can_write", False),
                    can_delete=permissions.get("can_delete", False),
                    created_by=created_by,
                    created_at=datetime.utcnow()
                )
                self.db.add(permission)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error setting group permission: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to set group permission"
            )

    async def log_access(
        self,
        user_id: int,
        knowledge_id: int,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log access to a resource."""
        try:
            # Create audit log
            audit = KnowledgeAudit(
                knowledge_id=knowledge_id,
                user_id=user_id,
                action=action,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging access: {str(e)}")
            # Don't raise exception for logging failures

# Global instance with dependency injection
def get_permission_service(db: Session = Depends(get_db)) -> PermissionService:
    """Get permission service instance."""
    return PermissionService(db)

permission_service = PermissionService() 