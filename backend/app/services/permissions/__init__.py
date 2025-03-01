"""Permissions services package."""

from app.services.permissions.service import PermissionService, permission_service

# Function to get the permission service singleton
def get_permission_service() -> PermissionService:
    """Get the permission service singleton instance."""
    return permission_service

__all__ = [
    "PermissionService",
    "permission_service",
    "get_permission_service",
] 