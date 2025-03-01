"""Token service implementation."""

import logging
from datetime import datetime
from typing import Optional

from redis import Redis
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.auth.interface import ITokenService

logger = logging.getLogger(__name__)

class TokenService(ITokenService):
    """Service for managing tokens."""

    def __init__(self):
        """Initialize token service with Redis connection."""
        self.redis: Optional[Redis] = None
        if settings.REDIS_HOST:
            try:
                self.redis = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")

    def _get_blacklist_key(self, token: str) -> str:
        """Get Redis key for blacklisted token."""
        return f"blacklist:token:{token}"

    async def blacklist_token(self, token: str, expires_in: int) -> None:
        """Add token to blacklist."""
        if not self.redis:
            logger.warning("Redis not available, token blacklisting disabled")
            return

        try:
            key = self._get_blacklist_key(token)
            self.redis.setex(key, expires_in, "blacklisted")
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process logout"
            )

    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        if not self.redis:
            return False

        try:
            key = self._get_blacklist_key(token)
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {str(e)}")
            return False

    async def cleanup_blacklist(self) -> None:
        """Clean up expired blacklisted tokens."""
        if not self.redis:
            return

        try:
            pattern = "blacklist:token:*"
            cursor = 0
            while True:
                cursor, keys = self.redis.scan(cursor, pattern)
                for key in keys:
                    if not self.redis.ttl(key):
                        self.redis.delete(key)
                if cursor == 0:
                    break
        except Exception as e:
            logger.error(f"Failed to cleanup token blacklist: {str(e)}")

token_service = TokenService() 