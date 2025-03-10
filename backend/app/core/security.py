"""Security middleware and utilities."""

import base64
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from app.core.config import settings
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from redis import Redis
from starlette.status import HTTP_403_FORBIDDEN

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer()

# Redis client for rate limiting
redis_client: Optional[Redis] = None
if settings.REDIS_HOST:
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
    )

# Prepare the API key encryption key
def prepare_fernet_key(key: str) -> bytes:
    """Prepare a Fernet key from a string, ensuring it's valid base64."""
    if settings.TESTING:
        # For testing, convert any string to a valid Fernet key
        # A valid Fernet key is 32 bytes, base64-encoded with URL-safe alphabet
        key_bytes = key.encode('utf-8')
        # Use the key as seed to generate 32 bytes
        import hashlib
        key_bytes = hashlib.sha256(key_bytes).digest()
        # Base64 encode with URL-safe alphabet
        return base64.urlsafe_b64encode(key_bytes)
    else:
        # In production, we expect a proper Fernet key
        return key.encode()

# Fernet instance for API key encryption
fernet = Fernet(prepare_fernet_key(settings.API_KEY_ENCRYPTION_KEY))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)


def create_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: str = settings.SECRET_KEY,
) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_password_reset_token(email: str) -> str:
    """Create password reset token."""
    delta = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return create_token(
        data={"sub": email, "type": "password_reset"},
        expires_delta=delta,
        secret_key=settings.SECRET_KEY_PASSWORD_RESET,
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token."""
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY_PASSWORD_RESET, algorithms=[settings.ALGORITHM]
        )
        if decoded_token["type"] != "password_reset":
            return None
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """Create email verification token."""
    delta = timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
    return create_token(
        data={"sub": email, "type": "email_verification"},
        expires_delta=delta,
        secret_key=settings.SECRET_KEY_EMAIL_VERIFICATION,
    )


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify email verification token."""
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY_EMAIL_VERIFICATION,
            algorithms=[settings.ALGORITHM],
        )
        if decoded_token["type"] != "email_verification":
            return None
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


async def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate API key."""
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is required"
        )
    try:
        # Decrypt and verify API key
        decrypted_key = fernet.decrypt(api_key.encode()).decode()
        # Add additional validation if needed
        return decrypted_key
    except Exception:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")


async def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict:
    """Get current user from JWT token."""
    try:
        token = credentials.credentials
        # Check if token is blacklisted - moved to token service
        # We'll check this in the routes that need it

        payload = await verify_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


def check_rate_limit(key: str) -> bool:
    """Check rate limiting for a given key."""
    if not settings.RATE_LIMIT_ENABLED or not redis_client:
        return True

    current = int(time.time())
    key = f"rate_limit:{key}"

    try:
        # Use Redis pipeline for atomic operations
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current - 60)  # Remove old requests
        pipe.zcard(key)  # Count requests in the last minute
        pipe.zadd(key, {str(current): current})
        pipe.expire(key, 60)  # Set TTL to clean up old keys
        results = pipe.execute()

        request_count = results[1]
        return request_count < settings.RATE_LIMIT_PER_MINUTE
    except Exception:
        # If Redis is unavailable, default to allowing the request
        return True


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key."""
    return fernet.encrypt(api_key.encode()).decode()


def generate_api_key() -> str:
    """Generate a new API key."""
    import secrets

    return secrets.token_urlsafe(32)
