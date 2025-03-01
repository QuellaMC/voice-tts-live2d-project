"""
Tests for user management endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_user(client):
    """Test creating a new user."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    
    # Store user ID for later tests
    return data["id"]


def test_get_users(client, admin_headers):
    """Test getting list of users (admin only)."""
    response = client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_user(client, user_headers):
    """Test getting a specific user."""
    # First create a user
    user_id = test_create_user(client)
    
    # Then get the user
    response = client.get(f"/api/v1/users/{user_id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert "username" in data
    assert "email" in data


def test_update_user(client, user_headers):
    """Test updating a user."""
    # First create a user
    user_id = test_create_user(client)
    
    # Then update the user
    update_data = {
        "username": "updatedusername",
        "email": "updated@example.com"
    }
    
    response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]


def test_me_endpoint(client, user_headers):
    """Test the /me endpoint."""
    response = client.get("/api/v1/users/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data


def test_change_password(client, user_headers):
    """Test changing password."""
    password_data = {
        "current_password": "testuser123",
        "new_password": "newpassword456"
    }
    
    response = client.post("/api/v1/users/me/change-password", json=password_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify login with new password works
    login_data = {
        "username": "testuser@test.com",  # Using email from fixture
        "password": "newpassword456"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200


def test_deactivate_user(client, admin_headers):
    """Test deactivating a user (admin only)."""
    # First create a user
    user_id = test_create_user(client)
    
    # Then deactivate the user
    response = client.post(f"/api/v1/users/{user_id}/deactivate", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify user is deactivated
    response = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False 