"""
Tests for root endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "Welcome to the AI Anime Companion API" in data["message"]


def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "data" in data
    assert "status" in data["data"]
    assert data["data"]["status"] == "healthy"
    assert "version" in data["data"]
