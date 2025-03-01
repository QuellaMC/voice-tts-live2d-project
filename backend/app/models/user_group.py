"""User group model definition."""

from datetime import datetime

from app.models.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

# Association table for user-group many-to-many relationship
user_group_members = Table(
    "user_group_members",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "group_id",
        Integer,
        ForeignKey("user_groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("added_at", DateTime, default=datetime.utcnow),
    Column("added_by", Integer, ForeignKey("users.id", ondelete="SET NULL")),
)


class UserGroup(Base):
    """User group model."""

    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    users = relationship("User", secondary=user_group_members, back_populates="groups")
    permissions = relationship(
        "GroupPermission", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of UserGroup."""
        return f"<UserGroup {self.name}>"
