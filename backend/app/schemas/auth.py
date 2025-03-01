"""Authentication schema models."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="Email address to send reset link to")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password"
    )

    @validator("new_password")
    def validate_password(cls, v):
        """Validate password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""

    email: EmailStr = Field(..., description="Email address to verify")
