"""User service implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    verify_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.database.session import get_db
from app.services.base import BaseService
from app.services.user.interface import IUserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class UserService(BaseService[User, UserCreate, UserUpdate], IUserService):
    """Service for managing users."""

    def __init__(self):
        """Initialize user service."""
        super().__init__(User)

    async def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email).first()

    async def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user."""
        # Validate passwords match
        obj_in.validate_passwords_match()
        
        # Create user object
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            email_verified=False,
            role=obj_in.role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate
    ) -> User:
        """Update a user."""
        update_data = obj_in.dict(exclude_unset=True)
        
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        update_data["updated_at"] = datetime.utcnow()
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    def create_access_token(self, *, user: User) -> str:
        """Create access token for user."""
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role
            },
            expires_delta=access_token_expires
        )

    async def update_password(
        self,
        db: Session,
        *,
        user: User,
        new_password: str
    ) -> User:
        """Update user password."""
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    async def verify_email(
        self,
        db: Session,
        *,
        user: User
    ) -> User:
        """Mark user email as verified."""
        user.email_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    async def get_current_user(
        self,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> Dict[str, Any]:
        """Get current authenticated user."""
        payload = await verify_token(token)
        user = await self.get(db, id=payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        } 