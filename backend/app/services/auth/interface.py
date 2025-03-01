"""Auth service interfaces."""

from abc import ABC, abstractmethod

class ITokenService(ABC):
    """Interface for token services."""

    @abstractmethod
    async def blacklist_token(self, token: str, expires_in: int) -> None:
        """Add token to blacklist."""
        pass

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        pass

    @abstractmethod
    async def cleanup_blacklist(self) -> None:
        """Clean up expired blacklisted tokens."""
        pass 