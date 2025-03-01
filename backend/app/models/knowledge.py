"""Knowledge base models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, ARRAY, Float, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

# Association tables
knowledge_tags = Table(
    'knowledge_tags',
    Base.metadata,
    Column('knowledge_id', Integer, ForeignKey('knowledge.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Index('ix_knowledge_tags_knowledge_id', 'knowledge_id'),
    Index('ix_knowledge_tags_tag_id', 'tag_id'),
    Index('ix_knowledge_tags_created_at', 'created_at')
)

knowledge_concepts = Table(
    'knowledge_concepts',
    Base.metadata,
    Column('knowledge_id', Integer, ForeignKey('knowledge.id', ondelete='CASCADE'), primary_key=True),
    Column('concept_id', Integer, ForeignKey('concepts.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Index('ix_knowledge_concepts_knowledge_id', 'knowledge_id'),
    Index('ix_knowledge_concepts_concept_id', 'concept_id'),
    Index('ix_knowledge_concepts_created_at', 'created_at')
)

class Knowledge(Base):
    """Knowledge model."""
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    question = Column(Text)
    answer = Column(Text)
    embedding = Column(ARRAY(Float))
    meta_info = Column(JSONB, default={})
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime)

    # Relationships
    tags = relationship("Tag", secondary=knowledge_tags, back_populates="knowledge_items")
    concepts = relationship("Concept", secondary=knowledge_concepts, back_populates="knowledge_items")
    audit_logs = relationship("KnowledgeAudit", back_populates="knowledge", cascade="all, delete-orphan")

    # Indexes and constraints
    __table_args__ = (
        Index('ix_knowledge_topic', 'topic'),
        Index('ix_knowledge_created_at', 'created_at'),
        Index('ix_knowledge_updated_at', 'updated_at'),
        Index('ix_knowledge_created_by', 'created_by'),
        CheckConstraint('length(topic) > 0', name='check_topic_not_empty'),
        CheckConstraint('length(content) > 0', name='check_content_not_empty'),
    )

class Tag(Base):
    """Tag model."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    knowledge_items = relationship("Knowledge", secondary=knowledge_tags, back_populates="tags")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes and constraints
    __table_args__ = (
        Index('ix_tags_name', 'name'),
        Index('ix_tags_created_at', 'created_at'),
        Index('ix_tags_created_by', 'created_by'),
        CheckConstraint("length(name) >= 2", name="tag_name_length_check"),
        CheckConstraint(
            "name ~ '^[a-zA-Z0-9_-]+$'",
            name="tag_name_format_check"
        ),
        {'extend_existing': True}
    )

class Concept(Base):
    """Concept model."""
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('concepts.id', ondelete='SET NULL'))
    level = Column(Integer, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    children = relationship("Concept", backref="parent", remote_side=[id])
    knowledge_items = relationship("Knowledge", secondary=knowledge_concepts, back_populates="concepts")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes and constraints
    __table_args__ = (
        Index('ix_concepts_name', 'name'),
        Index('ix_concepts_parent_id', 'parent_id'),
        Index('ix_concepts_level', 'level'),
        Index('ix_concepts_created_at', 'created_at'),
        Index('ix_concepts_created_by', 'created_by'),
        CheckConstraint("length(name) >= 2", name="concept_name_length_check"),
        CheckConstraint("level >= 0", name="concept_level_check"),
        CheckConstraint(
            "name ~ '^[a-zA-Z0-9_-]+$'",
            name="concept_name_format_check"
        ),
        {'extend_existing': True}
    )

class KnowledgeAudit(Base):
    """Knowledge audit model."""
    __tablename__ = "knowledge_audit"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_id = Column(Integer, ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(JSONB, default={})
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    knowledge = relationship("Knowledge", back_populates="audit_logs")
    user = relationship("User")

    # Indexes and constraints
    __table_args__ = (
        Index('ix_knowledge_audit_knowledge_id', 'knowledge_id'),
        Index('ix_knowledge_audit_user_id', 'user_id'),
        Index('ix_knowledge_audit_timestamp', 'timestamp'),
        Index('ix_knowledge_audit_action', 'action'),
        CheckConstraint(
            "action IN ('create', 'update', 'delete', 'access', 'cleanup')",
            name="audit_action_check"
        ),
        {'extend_existing': True}
    ) 