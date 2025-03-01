"""Email service implementation."""

import logging
from typing import Optional

from app.core.config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

logger = logging.getLogger(__name__)

# Check if email settings are configured
email_enabled = all(
    [
        settings.SMTP_USER,
        settings.SMTP_PASSWORD,
        settings.SMTP_FROM,
        settings.SMTP_PORT,
        settings.SMTP_HOST,
    ]
)

fastmail = None
if email_enabled:
    try:
        email_config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_FROM_NAME=settings.PROJECT_NAME,
            MAIL_STARTTLS=settings.SMTP_TLS,
            MAIL_SSL_TLS=not settings.SMTP_TLS,
            USE_CREDENTIALS=True,
        )
        fastmail = FastMail(email_config)
        logger.info("Email service configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure email service: {str(e)}")
        email_enabled = False
else:
    logger.warning(
        "Email service not configured. Email functionality will be disabled."
    )


async def send_email(
    email_to: EmailStr, subject: str, body: str, subtype: str = "html"
) -> None:
    """Send email using FastMail."""
    if not email_enabled or not fastmail:
        logger.warning(
            f"Email service not configured. Would have sent email to {email_to} with subject: {subject}"
        )
        return

    try:
        message = MessageSchema(
            subject=subject, recipients=[email_to], body=body, subtype=subtype
        )

        await fastmail.send_message(message)
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        # Don't raise the exception, just log it
        # This prevents the application from crashing if email sending fails


async def send_reset_password_email(email_to: EmailStr, token: str) -> None:
    """Send password reset email."""
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = f"{settings.PROJECT_NAME} - Password Reset"
    body = f"""
    <p>Hello,</p>
    <p>You have requested to reset your password.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <p>If you did not request this, please ignore this email.</p>
    <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
    <p>Best regards,<br>{settings.PROJECT_NAME} Team</p>
    """

    await send_email(email_to=email_to, subject=subject, body=body)


async def send_verification_email(email_to: EmailStr, token: str) -> None:
    """Send email verification email."""
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = f"{settings.PROJECT_NAME} - Email Verification"
    body = f"""
    <p>Hello,</p>
    <p>Thank you for registering with {settings.PROJECT_NAME}.</p>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verify_link}">{verify_link}</a></p>
    <p>If you did not create an account, please ignore this email.</p>
    <p>This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>
    <p>Best regards,<br>{settings.PROJECT_NAME} Team</p>
    """

    await send_email(email_to=email_to, subject=subject, body=body)
