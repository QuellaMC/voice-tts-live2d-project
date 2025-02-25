"""
Database models for the AI Anime Companion backend.
These models define the structure of the database.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """User model for authentication and personalization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    api_keys = relationship("UserApiKey", back_populates="user", cascade="all, delete-orphan")
    spaces = relationship("Space", back_populates="user", cascade="all, delete-orphan")

class ApiProvider(Base):
    """Model for supported API providers (OpenAI, Anthropic, etc.)."""
    __tablename__ = "api_providers"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String, unique=True, index=True)  # openai, anthropic, etc.
    name = Column(String)  # OpenAI, Anthropic, etc.
    description = Column(Text, nullable=True)
    default_endpoint = Column(String, nullable=True)  # Default API endpoint
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    admin_keys = relationship("AdminApiKey", back_populates="provider", cascade="all, delete-orphan")
    user_keys = relationship("UserApiKey", back_populates="provider", cascade="all, delete-orphan")

class AdminApiKey(Base):
    """Model for API keys managed by admins, shared among users."""
    __tablename__ = "admin_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("api_providers.id"))
    encrypted_key = Column(String)
    custom_endpoint = Column(String, nullable=True)
    added_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    # Relationships
    provider = relationship("ApiProvider", back_populates="admin_keys")
    admin = relationship("User", foreign_keys=[added_by])

class UserApiKey(Base):
    """Model for user-specific API keys."""
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider_id = Column(Integer, ForeignKey("api_providers.id"))
    encrypted_key = Column(String)
    custom_endpoint = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    provider = relationship("ApiProvider", back_populates="user_keys")

class Space(Base):
    """Model for user spaces/characters."""
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    live2d_model = Column(String, nullable=True)
    voice_model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)
    settings = Column(JSON, nullable=True)  # Store various settings as JSON

    # API provider preferences
    llm_provider_id = Column(Integer, ForeignKey("api_providers.id"), nullable=True)
    tts_provider_id = Column(Integer, ForeignKey("api_providers.id"), nullable=True)
    
    # Whether to use user's keys, admin keys, or default
    use_user_llm_key = Column(Boolean, default=False)
    use_user_tts_key = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="spaces")
    llm_provider = relationship("ApiProvider", foreign_keys=[llm_provider_id])
    tts_provider = relationship("ApiProvider", foreign_keys=[tts_provider_id])
    conversations = relationship("Conversation", back_populates="space", cascade="all, delete-orphan")

class Conversation(Base):
    """Model for conversation history."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message = Column(DateTime, nullable=True)
    title = Column(String, nullable=True)

    # Relationships
    space = relationship("Space", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Model for individual messages in a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    audio_url = Column(String, nullable=True)  # URL to synthesized audio

    # Relationships
    conversation = relationship("Conversation", back_populates="messages") 