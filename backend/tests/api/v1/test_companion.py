"""
Tests for companion endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from tests.mocks import mock_companion_service


def test_create_companion(client, user_headers, mock_companion_service):
    """Test creating a new companion."""
    companion_data = {
        "name": "Test Companion",
        "description": "A test companion for unit testing",
        "personality": "Friendly and helpful",
        "voice_id": "test-voice-id",
        "live2d_model": "test-model-id",
    }

    response = client.post(
        "/api/v1/companion/companions", json=companion_data, headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == companion_data["name"]
    assert data["description"] == companion_data["description"]

    # Store companion ID for later tests
    return data["id"]


def test_list_companions(client, user_headers, mock_companion_service):
    """Test listing companions."""
    response = client.get("/api/v1/companion/companions", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least one companion (created in previous test)
    assert len(data) > 0


def test_get_companion(client, user_headers, mock_companion_service):
    """Test getting a specific companion."""
    # First create a companion
    companion_id = test_create_companion(client, user_headers, mock_companion_service)

    # Then retrieve it
    response = client.get(
        f"/api/v1/companion/companions/{companion_id}", headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == companion_id
    assert "name" in data
    assert "description" in data


def test_update_companion(client, user_headers, mock_companion_service):
    """Test updating a companion."""
    # First create a companion
    companion_id = test_create_companion(client, user_headers, mock_companion_service)

    # Then update it
    update_data = {
        "name": "Updated Companion Name",
        "description": "Updated description",
    }

    response = client.put(
        f"/api/v1/companion/companions/{companion_id}",
        json=update_data,
        headers=user_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_chat_with_companion(client, user_headers, mock_companion_service):
    """Test chatting with a companion."""
    # First create a companion
    companion_id = test_create_companion(client, user_headers, mock_companion_service)

    # Then chat with it
    chat_data = {"message": "Hello, how are you?", "companion_id": companion_id}

    response = client.post(
        "/api/v1/companion/chat", json=chat_data, headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_delete_companion(client, user_headers, mock_companion_service):
    """Test deleting a companion."""
    # First create a companion
    companion_id = test_create_companion(client, user_headers, mock_companion_service)

    # Then delete it
    response = client.delete(
        f"/api/v1/companion/companions/{companion_id}", headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Verify it's deleted
    response = client.get(
        f"/api/v1/companion/companions/{companion_id}", headers=user_headers
    )
    assert response.status_code == 404
