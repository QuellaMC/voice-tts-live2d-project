"""
Dependencies for FastAPI route handlers.
This module provides dependency functions for authentication and API key management.
"""

import logging
import os
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, Optional, Tuple

from app.database.session import get_db
from app.models.models import UserRole
from app.models.user import User
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme for bearer token authentication
security = HTTPBearer()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)  # 24 hours


def create_access_token(data: Dict) -> str:
    """Create a JWT access token with expiration."""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token",
        )


@lru_cache(maxsize=1000)
def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token with caching."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing authentication token",
        )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempted access: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        try:
            user.last_login = datetime.utcnow()
            db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating last login: {str(e)}")
            db.rollback()

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure the current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user attempted admin action: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )

    return current_user


async def validate_api_key_access(
    provider: str, current_user: User = Depends(get_current_user)
) -> Tuple[bool, User]:
    """
    Validate that a user has access to manage API keys for a provider.
    Returns both the validation result and the user object for efficiency.
    """
    try:
        # Admin users can manage all API keys
        if current_user.role == UserRole.ADMIN:
            return True, current_user

        # Check if provider is valid
        valid_providers = {"openai", "anthropic", "elevenlabs", "azure"}
        if provider not in valid_providers:
            logger.warning(f"Invalid API provider requested: {provider}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid API provider"
            )

        # For now, allow all authenticated users to manage their own keys
        return True, current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API key access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating API key access",
        )
