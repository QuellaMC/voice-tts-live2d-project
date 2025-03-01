"""User management endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_api_key
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserList
)
from app.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get current user information."""
    user = await UserService().get(db, id=current_user["id"])
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> UserResponse:
    """Get user by ID."""
    user = await UserService().get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.get("/", response_model=UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> UserList:
    """List users with pagination and optional search."""
    filters = {}
    if search:
        filters["email"] = search

    users = await UserService().get_multi(
        db,
        skip=skip,
        limit=limit,
        filters=filters
    )
    total = await UserService().count(db, filters=filters)
    
    return UserList(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> UserResponse:
    """Create new user."""
    # Check if email already exists
    existing_user = await UserService().get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    user = await UserService().create(db, obj_in=user_in)
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> UserResponse:
    """Update user information."""
    user = await UserService().get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Only allow users to update their own information unless they're admin
    if user_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    user = await UserService().update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> UserResponse:
    """Delete user."""
    # Only admins can delete users
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    user = await UserService().delete(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.post("/login")
async def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
) -> dict:
    """Authenticate user and return access token."""
    user = await UserService().authenticate(db, email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    
    access_token = UserService().create_access_token(user=user)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 