"""User schemas for request/response models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    role: str = "user"


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: constr(min_length=8)
    password_confirm: str

    def validate_passwords_match(self):
        """Validate that passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[constr(min_length=8)] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserInDB(UserBase):
    """Schema for user in database."""

    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserList(BaseModel):
    """Schema for paginated user list."""

    items: List[UserResponse]
    total: int
    skip: int
    limit: int

    class Config:
        orm_mode = True
