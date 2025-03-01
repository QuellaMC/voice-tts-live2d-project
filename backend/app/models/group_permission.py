"""Group permission model definition."""

from datetime import datetime

from app.models.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class GroupPermission(Base):
    """Group permission model."""

    __tablename__ = "group_permissions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(
        Integer, ForeignKey("user_groups.id", ondelete="CASCADE"), nullable=False
    )
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    can_read = Column(Boolean, default=True, nullable=False)
    can_write = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    group = relationship("UserGroup", back_populates="permissions")

    def __repr__(self) -> str:
        """String representation of GroupPermission."""
        return f"<GroupPermission {self.group_id} - {self.resource_type}>"

    class Config:
        """Model configuration."""

        indexes = [("group_id", "resource_type", "resource_id")]
