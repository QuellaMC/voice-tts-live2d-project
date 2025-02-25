"""
Dependencies for FastAPI route handlers.
This module provides dependency functions for authentication and API key management.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from jose import jwt, JWTError
from typing import Dict, Optional
from datetime import datetime, timedelta

# Security scheme for bearer token authentication
security = HTTPBearer()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Role definitions
class UserRole:
    ADMIN = "admin"
    USER = "user"

def create_access_token(data: Dict) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real implementation, you'd fetch the user from database
    # For now, just return user_id
    return user_id

async def get_current_admin(user_id: str = Depends(get_current_user)):
    """Dependency to ensure the current user is an admin."""
    # In a real implementation, you'd check user roles in database
    # For now, this is a placeholder
    is_admin = True  # Replace with actual admin check
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
    
    return user_id

async def validate_api_key_access(
    provider: str, 
    user_id: str = Depends(get_current_user)
) -> bool:
    """
    Validate that a user has access to manage API keys for a provider.
    Used for API endpoints that modify user-specific API keys.
    """
    # In a real implementation, check if the user has permissions
    # to manage keys for this provider
    return True 