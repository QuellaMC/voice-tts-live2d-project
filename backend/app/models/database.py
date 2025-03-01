from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import Index

Base = declarative_base()


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


# Association tables
knowledge_tags = Table(
    "knowledge_tags",
    Base.metadata,
    Column(
        "knowledge_id",
        Integer,
        ForeignKey("knowledge.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)

knowledge_concepts = Table(
    "knowledge_concepts",
    Base.metadata,
    Column(
        "knowledge_id",
        Integer,
        ForeignKey("knowledge.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "concept_id",
        Integer,
        ForeignKey("concepts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Concept(Base):
    """Hierarchical concept model for organizing knowledge."""

    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    level = Column(Integer, nullable=False)  # Hierarchy level (0 = root)
    description = Column(Text, nullable=True)

    # Relationships
    children = relationship("Concept", backref="parent", remote_side=[id])
    knowledge_entries = relationship(
        "Knowledge", secondary=knowledge_concepts, back_populates="concepts"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "level": self.level,
            "description": self.description,
            "children": [child.to_dict() for child in self.children],
        }


class User(Base):
    """User model with role-based access control."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(100), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(255), nullable=False)
    role: UserRole = Column(
        SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER
    )
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login: Optional[datetime] = Column(DateTime, nullable=True)

    # Relationships
    groups: List["UserGroup"] = relationship(
        "UserGroup", secondary="user_group_members", back_populates="users"
    )
    audit_logs: List["KnowledgeAudit"] = relationship(
        "KnowledgeAudit", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Knowledge(Base):
    """Knowledge entry database model with vector embeddings."""

    __tablename__ = "knowledge"

    id: int = Column(Integer, primary_key=True)
    topic: str = Column(String(200), unique=True, nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    question: Optional[str] = Column(Text, nullable=True)
    answer: Optional[str] = Column(Text, nullable=True)
    embedding: Optional[List[float]] = Column(ARRAY(Float), nullable=True)
    metadata: Optional[dict] = Column(JSONB, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: str = Column(String(100), nullable=False)

    # Relationships with cascade delete
    tags: List["Tag"] = relationship(
        "Tag",
        secondary=knowledge_tags,
        back_populates="knowledge_entries",
        cascade="all, delete",
    )
    concepts: List["Concept"] = relationship(
        "Concept",
        secondary=knowledge_concepts,
        back_populates="knowledge_entries",
        cascade="all, delete",
    )
    audit_logs: List["KnowledgeAudit"] = relationship(
        "KnowledgeAudit", back_populates="knowledge", cascade="all, delete"
    )

    __table_args__ = (
        Index("ix_knowledge_embedding", "embedding", postgresql_using="gin"),
        Index("ix_knowledge_created_at", "created_at"),
        Index("ix_knowledge_updated_at", "updated_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "content": self.content,
            "question": self.question,
            "answer": self.answer,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "tags": [tag.name for tag in self.tags],
            "concepts": [concept.name for concept in self.concepts],
        }


class Tag(Base):
    """Tag model for categorizing knowledge entries."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    knowledge_entries = relationship(
        "Knowledge", secondary=knowledge_tags, back_populates="tags"
    )

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description}


class UserGroup(Base):
    """Group model for organizing users and permissions."""

    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    users = relationship(
        "User", secondary="user_group_members", back_populates="groups"
    )
    permissions = relationship(
        "GroupPermission", back_populates="group", cascade="all, delete-orphan"
    )


class UserGroupMember(Base):
    """Association table for users and groups."""

    __tablename__ = "user_group_members"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("user_groups.id"), primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, ForeignKey("users.id"))


class GroupPermission(Base):
    """Permissions for knowledge base access by group."""

    __tablename__ = "group_permissions"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("user_groups.id"))
    resource_type = Column(String(50))  # e.g., 'knowledge', 'concept', 'tag'
    resource_id = Column(Integer, nullable=True)  # Specific resource ID or null for all
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    group = relationship("UserGroup", back_populates="permissions")


class KnowledgeAudit(Base):
    """Audit trail for knowledge base operations."""

    __tablename__ = "knowledge_audit"

    id = Column(Integer, primary_key=True)
    knowledge_id = Column(Integer, ForeignKey("knowledge.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))  # e.g., 'create', 'read', 'update', 'delete'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSONB, nullable=True)  # Additional audit information

    # Relationships
    knowledge = relationship("Knowledge")
    user = relationship("User")


# Update User model to include group relationship
User.groups = relationship(
    "UserGroup", secondary="user_group_members", back_populates="users"
)

# Update Knowledge model to include audit relationship
Knowledge.audit_logs = relationship("KnowledgeAudit", back_populates="knowledge")
