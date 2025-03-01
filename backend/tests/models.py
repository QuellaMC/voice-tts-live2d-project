"""Test-specific models for SQLite compatibility."""

import enum
from datetime import datetime
import json

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Float,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model for testing."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class APIKey(Base):
    """API key model for testing."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    key_hash = Column(String, index=True)
    name = Column(String)
    scopes = Column(String)  # Comma-separated list of scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class Knowledge(Base):
    """Knowledge model for testing - with TEXT instead of ARRAY for SQLite compatibility."""

    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    question = Column(Text)
    answer = Column(Text)
    # Store embedding as JSON string instead of ARRAY for SQLite compatibility
    embedding = Column(Text)  
    meta_info = Column(JSON, default={})
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime)

    # Helper methods for embedding conversion
    def set_embedding(self, embedding_array):
        """Convert embedding array to JSON string."""
        if embedding_array is not None:
            self.embedding = json.dumps(embedding_array)
        
    def get_embedding(self):
        """Convert JSON string back to array."""
        if self.embedding:
            return json.loads(self.embedding)
        return None


class Tag(Base):
    """Tag model for testing."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Concept(Base):
    """Concept model for testing."""

    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("concepts.id", ondelete="SET NULL"))
    level = Column(Integer, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Companion(Base):
    """Companion model for testing."""

    __tablename__ = "companions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    voice_id = Column(String, nullable=True)
    live2d_model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow) 