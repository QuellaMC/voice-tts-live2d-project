"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_main_root_endpoint():
    """Test the main app's root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "Welcome to the Voice TTS Live2D Project API" in data["message"]
    assert "data" in data
    assert "api_url" in data["data"]
    assert "docs_url" in data["data"]


def test_main_health_check():
    """Test the main app's health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
