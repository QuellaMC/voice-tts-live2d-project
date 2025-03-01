"""User service interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class IUserService(ABC):
    """Interface for user services."""

    @abstractmethod
    async def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user."""
        pass

    @abstractmethod
    async def get_by_email(
        self,
        db: Session,
        *,
        email: str
    ) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def create(
        self,
        db: Session,
        *,
        obj_in: UserCreate
    ) -> User:
        """Create new user."""
        pass

    @abstractmethod
    async def update_password(
        self,
        db: Session,
        *,
        user: User,
        new_password: str
    ) -> User:
        """Update user password."""
        pass

    @abstractmethod
    async def verify_email(
        self,
        db: Session,
        *,
        user: User
    ) -> User:
        """Mark user email as verified."""
        pass

    @abstractmethod
    async def get_current_user(
        self,
        db: Session,
        token: str
    ) -> Dict[str, Any]:
        """Get current authenticated user."""
        pass 