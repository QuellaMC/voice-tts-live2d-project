"""Main application module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings, validate_settings
from app.core.monitoring import setup_monitoring, cleanup_monitoring
from app.database.session import init_db, cleanup_db
from app.api.v1.router import api_router
from app.schemas.response import ResponseBase

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    try:
        # Validate settings
        validate_settings()
        
        # Initialize components
        init_db()
        logger.info("Application startup completed")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Cleanup on shutdown
        cleanup_db()
        cleanup_monitoring()
        logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title=settings.SERVER_NAME,
    version="1.0.0",
    description="Backend API for Voice TTS Live2D Project",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Set up security middleware - only use TrustedHostMiddleware in production
if settings.ENV_NAME != "development":
    # In production, use the configured CORS origins
    allowed_hosts = [str(host) for host in settings.BACKEND_CORS_ORIGINS] or ["*"]
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up monitoring
setup_monitoring(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add root endpoint to redirect to API
@app.get("/", response_model=ResponseBase)
async def root():
    """Root endpoint that welcomes users and directs them to the API."""
    return {
        "success": True, 
        "message": "Welcome to the Voice TTS Live2D Project API", 
        "data": {
            "api_url": f"{settings.SERVER_HOST}{settings.API_V1_STR}/",
            "docs_url": f"{settings.SERVER_HOST}/api/docs"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path
        }
    )

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENV_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
        server_header=False,
        date_header=False
    )
