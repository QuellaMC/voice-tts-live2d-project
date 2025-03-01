"""Base model class for SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import as_declarative, declared_attr

T = TypeVar("T")


@as_declarative()
class Base:
    """Base class for all SQLAlchemy models."""

    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary."""
        return cls(**data)


class TimestampMixin:
    """Mixin to add created_at and updated_at fields."""

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UUIDMixin:
    """Mixin to add UUID field."""

    uuid = Column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
