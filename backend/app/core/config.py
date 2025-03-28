"""Application configuration management."""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment
    ENV_NAME: str = "development"
    DEBUG: bool = False
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    # Application
    PROJECT_NAME: str = "Voice TTS Live2D"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str = "Voice TTS Live2D API"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY_PASSWORD_RESET: str = secrets.token_urlsafe(32)
    SECRET_KEY_EMAIL_VERIFICATION: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[AnyHttpUrl], List[str]]:
        """Validate and process CORS origins from different input formats."""
        import json
        import logging

        # Default safe origins if parsing fails
        default_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]

        # If it's already a list, return it directly
        if isinstance(v, list):
            return v

        # Handle string input
        if isinstance(v, str):
            # Try parsing as JSON if it looks like a JSON array
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse CORS origins as JSON: {v}")

            # Handle comma-separated format
            if "," in v:
                origins = [i.strip() for i in v.split(",") if i.strip()]
                logging.info(
                    f"Parsed CORS origins from comma-separated string: {origins}"
                )
                return origins

            # Handle single origin
            if v.strip():
                logging.info(f"Using single CORS origin: {v.strip()}")
                return [v.strip()]

        # Log warning and return default origins for any other case
        logging.warning(f"Using default CORS origins due to invalid format: {v}")
        return default_origins

    @validator("BACKEND_CORS_ORIGINS", each_item=True)
    def validate_cors_origins(cls, v: Any) -> Any:
        """Convert string origins to AnyHttpUrl if possible, otherwise keep as string."""
        # If it's already a valid AnyHttpUrl, return it
        if isinstance(v, AnyHttpUrl):
            return v

        # Handle string urls by trying to parse them, but keep them as strings if they don't parse
        if isinstance(v, str) and v:
            try:
                # Try to validate as an AnyHttpUrl
                return AnyHttpUrl(v)
            except ValueError:
                import logging

                logging.warning(f"CORS origin not a valid URL, keeping as string: {v}")
                return v

        return v

    # Database
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[Union[PostgresDsn, str]] = None
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    @validator(
        "POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", pre=True
    )
    def set_db_fields_for_testing(
        cls, v: Optional[str], values: Dict[str, Any], **kwargs
    ) -> Any:
        """Set default values for database fields during testing."""
        field_name = kwargs["field"].name
        if values.get("TESTING", False) and v is None:
            if field_name == "POSTGRES_SERVER":
                return "localhost"
            elif field_name == "POSTGRES_USER":
                return "postgres"
            elif field_name == "POSTGRES_PASSWORD":
                return "postgres"
            elif field_name == "POSTGRES_DB":
                return "test_db"
        return v

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble database connection URI."""
        if isinstance(v, str):
            # If we're testing and using SQLite, don't validate as PostgresDsn
            if values.get("TESTING", False) and v and v.startswith("sqlite:"):
                return v
            return v

        # For testing, use the TEST_DATABASE_URL environment variable if available
        if values.get("TESTING", False):
            test_db_url = os.getenv("TEST_DATABASE_URL")
            if test_db_url:
                # If using SQLite for tests, return as is
                if test_db_url.startswith("sqlite:"):
                    return test_db_url
                return test_db_url

        # Otherwise build the connection string from components
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT", 5432)),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Redis and Caching
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 60 * 5  # 5 minutes
    CACHE_MAX_SIZE: int = 10000

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[EmailStr] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Monitoring
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831
    SENTRY_DSN: Optional[str] = None
    METRICS_ENABLED: bool = True
    METRICS_AUTH_REQUIRED: bool = True
    METRICS_USERNAME: Optional[str] = None
    METRICS_PASSWORD: Optional[str] = None

    @validator("SENTRY_DSN", pre=True)
    def validate_sentry_dsn(cls, v: Any) -> Optional[str]:
        """Validate Sentry DSN, allowing None or empty string values."""
        import logging

        # Handle None or empty string
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        # If it's a string with a value, return as is
        if isinstance(v, str):
            # Very basic URL validation to ensure it has a scheme
            if not (v.startswith("http://") or v.startswith("https://")):
                logging.warning(
                    f"Invalid Sentry DSN format (missing scheme): {v}, setting to None"
                )
                return None
            return v

        return None

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "test_secret_key_for_testing_only")
    JWT_ALGORITHM: str = "HS256"
    API_KEY_ENCRYPTION_KEY: str = os.getenv(
        "API_KEY_ENCRYPTION_KEY", "test_key_for_testing_only_1234567890123456"
    )
    SECURITY_BCRYPT_ROUNDS: int = 12

    # External Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    AZURE_TTS_KEY: Optional[str] = None
    AZURE_TTS_REGION: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    RATE_LIMIT_ENABLED: bool = True

    # Static files
    STATIC_DIR: str = "static"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None

    @validator("REDIS_HOST")
    def validate_redis_settings(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """Validate Redis settings when rate limiting is enabled."""
        if (
            values.get("RATE_LIMIT_ENABLED", False)
            and not v
            and not values.get("TESTING", False)
        ):
            raise ValueError("Redis host is required when rate limiting is enabled")
        return v

    @validator("SMTP_HOST")
    def validate_email_settings(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """Validate email settings."""
        if (
            any(
                [
                    values.get("SMTP_USER"),
                    values.get("SMTP_PASSWORD"),
                    values.get("EMAILS_FROM_EMAIL"),
                ]
            )
            and not v
            and not values.get("TESTING", False)
        ):
            raise ValueError("SMTP host is required when email settings are provided")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()


def validate_settings() -> None:
    """Validate that all required settings are properly configured."""
    # Skip validation during testing
    if settings.TESTING:
        return

    required_settings = [
        ("JWT_SECRET", "JWT secret key is required for authentication"),
        (
            "API_KEY_ENCRYPTION_KEY",
            "API key encryption key is required for secure storage",
        ),
        ("POSTGRES_SERVER", "Database server address is required"),
        ("POSTGRES_USER", "Database username is required"),
        ("POSTGRES_PASSWORD", "Database password is required"),
        ("POSTGRES_DB", "Database name is required"),
        ("SERVER_NAME", "Server name is required"),
        ("SERVER_HOST", "Server host URL is required"),
    ]

    # Only require metrics authentication if metrics auth is enabled and not in development
    if settings.METRICS_AUTH_REQUIRED and settings.ENV_NAME != "development":
        required_settings.extend(
            [
                ("METRICS_USERNAME", "Metrics authentication username is required"),
                ("METRICS_PASSWORD", "Metrics authentication password is required"),
            ]
        )

    # Only require Redis if rate limiting is enabled and not in development
    if settings.RATE_LIMIT_ENABLED and settings.ENV_NAME != "development":
        required_settings.extend(
            [
                ("REDIS_HOST", "Redis host is required for rate limiting"),
                ("REDIS_PORT", "Redis port is required for rate limiting"),
            ]
        )

    missing_settings = []
    for setting, message in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(message)

    if missing_settings:
        raise ValueError(
            "Missing required settings:\n"
            + "\n".join(f"- {msg}" for msg in missing_settings)
        )
