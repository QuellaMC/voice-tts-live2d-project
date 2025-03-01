"""
Basic tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()
    assert "environment" in response.json()


def test_api_docs():
    """Test the API documentation endpoint."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema():
    """Test the OpenAPI schema endpoint."""
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "components" in schema
