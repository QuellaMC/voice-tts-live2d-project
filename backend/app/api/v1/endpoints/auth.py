"""Authentication endpoints."""

from datetime import timedelta
from typing import Optional

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.database.session import get_db
from app.schemas.auth import (
    EmailVerificationRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
)
from app.schemas.response import ResponseBase, TokenResponse
from app.services.auth.email import send_reset_password_email, send_verification_email
from app.services.auth.token import token_service
from app.services.user import UserService
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenResponse:
    """Authenticate user and return access token."""
    user = await UserService().authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is not active"
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified"
        )

    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: dict = Depends(UserService().get_current_user),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Refresh access token."""
    user = await UserService().get(db, id=current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is not active"
        )

    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", expires_in=expires_in
    )


@router.post("/logout", response_model=ResponseBase)
async def logout(
    request: Request,
    current_user: dict = Depends(UserService().get_current_user),
    db: Session = Depends(get_db),
) -> ResponseBase:
    """Logout user and invalidate token."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        await token_service.blacklist_token(
            token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    return ResponseBase(success=True, message="Successfully logged out")


@router.post("/password-reset/request", response_model=ResponseBase)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ResponseBase:
    """Request password reset."""
    user = await UserService().get_by_email(db, email=request.email)
    if user and user.is_active:
        token = create_password_reset_token(user.email)
        background_tasks.add_task(
            send_reset_password_email, email_to=user.email, token=token
        )

    return ResponseBase(
        success=True, message="If the email exists, a password reset link will be sent"
    )


@router.post("/password-reset/confirm", response_model=ResponseBase)
async def confirm_password_reset(
    request: PasswordResetConfirm, db: Session = Depends(get_db)
) -> ResponseBase:
    """Reset password using reset token."""
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = await UserService().get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active"
        )

    await UserService().update_password(
        db, user=user, new_password=request.new_password
    )

    return ResponseBase(success=True, message="Password has been reset successfully")


@router.post("/verify-email/request", response_model=ResponseBase)
async def request_email_verification(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ResponseBase:
    """Request email verification."""
    user = await UserService().get_by_email(db, email=request.email)
    if user and user.is_active and not user.email_verified:
        token = create_password_reset_token(user.email)
        background_tasks.add_task(
            send_verification_email, email_to=user.email, token=token
        )

    return ResponseBase(
        success=True,
        message="If the email exists and is not verified, a verification link will be sent",
    )


@router.post("/verify-email/confirm/{token}", response_model=ResponseBase)
async def confirm_email(token: str, db: Session = Depends(get_db)) -> ResponseBase:
    """Verify email using verification token."""
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user = await UserService().get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active"
        )

    if user.email_verified:
        return ResponseBase(success=True, message="Email already verified")

    await UserService().verify_email(db, user=user)

    return ResponseBase(success=True, message="Email verified successfully")
