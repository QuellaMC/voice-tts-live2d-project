"""Application monitoring and observability configuration."""

import logging
import time
import os
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, REGISTRY
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app.core.config import settings

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

DB_OPERATION_LATENCY = Histogram(
    "db_operation_duration_seconds",
    "Database operation latency in seconds",
    ["operation", "table"]
)

# Global variables for cleanup
tracer_provider = None
otlp_exporter = None

def setup_tracing(app: FastAPI) -> None:
    """Configure OpenTelemetry tracing."""
    global tracer_provider, otlp_exporter

    # Skip tracing setup in test mode
    if os.environ.get("TESTING") == "true":
        logger.info("Skipping tracing setup in test mode")
        return

    if settings.JAEGER_HOST:
        try:
            tracer_provider = TracerProvider()
            
            # Use OTLP exporter instead of Jaeger exporter
            otlp_endpoint = f"http://{settings.JAEGER_HOST}:4317"
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            
            tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            trace.set_tracer_provider(tracer_provider)

            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app)
            # Instrument SQLAlchemy
            SQLAlchemyInstrumentor().instrument()

            logger.info(f"Tracing configured successfully with OTLP exporter to {otlp_endpoint}")
        except Exception as e:
            logger.error(f"Failed to configure tracing: {str(e)}")

async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """Collect request metrics."""
    start_time = time.time()
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
        status = response.status_code
    except Exception as e:
        status = 500
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

    return response

def setup_monitoring(app: FastAPI) -> None:
    """Configure application monitoring."""
    # Add metrics middleware
    app.middleware("http")(metrics_middleware)

    # Add metrics endpoint with authentication if required
    if settings.METRICS_AUTH_REQUIRED:
        from fastapi import Depends, HTTPException, status
        from fastapi.security import HTTPBasic, HTTPBasicCredentials
        import secrets

        security = HTTPBasic()

        def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
            # Check if metrics username and password are set
            if not settings.METRICS_USERNAME or not settings.METRICS_PASSWORD:
                logger.warning("Metrics authentication is required but credentials are not set")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Metrics authentication is misconfigured"
                )
                
            correct_username = secrets.compare_digest(
                credentials.username, settings.METRICS_USERNAME
            )
            correct_password = secrets.compare_digest(
                credentials.password, settings.METRICS_PASSWORD
            )
            if not (correct_username and correct_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Basic"},
                )
            return True

        @app.get("/metrics", dependencies=[Depends(verify_auth)])
        async def metrics():
            from prometheus_client import generate_latest
            return Response(
                generate_latest(),
                media_type="text/plain"
            )
    else:
        @app.get("/metrics")
        async def metrics():
            from prometheus_client import generate_latest
            return Response(
                generate_latest(),
                media_type="text/plain"
            )

    # Setup tracing if configured
    setup_tracing(app)
    logger.info("Monitoring configured successfully")

def record_db_operation(operation: str, table: str, duration: float) -> None:
    """Record database operation metrics."""
    DB_OPERATION_LATENCY.labels(operation=operation, table=table).observe(duration)

def cleanup_monitoring() -> None:
    """Cleanup monitoring resources."""
    try:
        # Clear Prometheus metrics
        for collector in list(REGISTRY._collector_to_names.keys()):
            REGISTRY.unregister(collector)

        # Cleanup tracing
        if tracer_provider:
            tracer_provider.shutdown()
        if otlp_exporter:
            otlp_exporter.shutdown()

        logger.info("Monitoring resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during monitoring cleanup: {str(e)}") 