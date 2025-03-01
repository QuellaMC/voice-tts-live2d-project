"""Application middleware."""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.config import settings
from app.core.security import check_rate_limit

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Track requests with unique IDs."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()
        
        response = await call_next(request)
        
        # Add request tracking headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(time.time() - request.state.start_time)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit requests by IP and path."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0]
        else:
            client_ip = request.client.host

        # Create rate limit key based on IP and path
        rate_limit_key = f"{client_ip}:{request.url.path}"

        # Check rate limit
        if not check_rate_limit(rate_limit_key):
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )

        return await call_next(request)

def setup_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add request tracking
    app.add_middleware(RequestTrackingMiddleware)

    # Add rate limiting
    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)

    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[str(host) for host in settings.BACKEND_CORS_ORIGINS]
    ) 