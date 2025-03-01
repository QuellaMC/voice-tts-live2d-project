"""
Router for managing user groups and permissions.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.api import APIResponse
from app.core.dependencies import get_current_admin, get_current_user
from app.services.permissions import get_permission_service
from sqlalchemy.orm import Session
from app.core.security import get_api_key
from app.database.session import get_db
from app.models.user_group import UserGroup
from app.models.group_permission import GroupPermission

class GroupCreate(BaseModel):
    """Request model for creating a new user group."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class GroupUpdate(BaseModel):
    """Request model for updating a user group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class PermissionSet(BaseModel):
    """Request model for setting group permissions."""
    resource_type: str = Field(..., description="Type of resource (knowledge, concept, tag)")
    resource_id: Optional[int] = Field(None, description="Specific resource ID or null for all")
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False

router = APIRouter(prefix="/groups", tags=["User Groups"])

@router.post("/create", response_model=APIResponse)
async def create_group(
    name: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Create a new user group."""
    # TODO: Implement group creation
    raise HTTPException(
        status_code=501,
        detail="Not implemented yet"
    )

@router.get("/list", response_model=APIResponse)
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """List user groups."""
    # TODO: Implement group listing
    raise HTTPException(
        status_code=501,
        detail="Not implemented yet"
    )

@router.put("/{group_id}/update", response_model=APIResponse)
async def update_group(
    group_id: int,
    data: GroupUpdate,
    current_user: str = Depends(get_current_admin)
):
    """Update a user group.
    
    Args:
        group_id: ID of the group to update
        data: Group update data
        current_user: Admin user updating the group
        
    Returns:
        APIResponse: Contains updated group information
    """
    from models.database import UserGroup
    
    group = get_permission_service().db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if data.name is not None:
        group.name = data.name
    if data.description is not None:
        group.description = data.description
        
    get_permission_service().db.commit()
    
    return {
        "status": "success",
        "data": {"id": group.id, "name": group.name},
        "message": f"Group updated successfully."
    }

@router.post("/{group_id}/permissions", response_model=APIResponse)
async def set_group_permissions(
    group_id: int,
    permissions: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> dict:
    """Set permissions for a user group."""
    # TODO: Implement permission setting
    raise HTTPException(
        status_code=501,
        detail="Not implemented yet"
    )

@router.post("/{group_id}/users/add", response_model=APIResponse)
async def add_users_to_group(
    group_id: int,
    user_ids: List[int],
    current_user: str = Depends(get_current_admin)
):
    """Add users to a group.
    
    Args:
        group_id: ID of the group
        user_ids: List of user IDs to add
        current_user: Admin user performing the action
        
    Returns:
        APIResponse: Contains confirmation message
    """
    for user_id in user_ids:
        get_permission_service().add_user_to_group(
            user_id=user_id,
            group_id=group_id,
            added_by=current_user.id
        )
    
    return {
        "status": "success",
        "message": f"Added {len(user_ids)} users to the group."
    }

@router.post("/{group_id}/users/remove", response_model=APIResponse)
async def remove_users_from_group(
    group_id: int,
    user_ids: List[int],
    current_user: str = Depends(get_current_admin)
):
    """Remove users from a group.
    
    Args:
        group_id: ID of the group
        user_ids: List of user IDs to remove
        current_user: Admin user performing the action
        
    Returns:
        APIResponse: Contains confirmation message
    """
    for user_id in user_ids:
        get_permission_service().remove_user_from_group(
            user_id=user_id,
            group_id=group_id
        )
    
    return {
        "status": "success",
        "message": f"Removed {len(user_ids)} users from the group."
    } 