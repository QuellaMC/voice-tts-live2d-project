"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch


class MockUser:
    """Mock User class with the attributes needed by the auth endpoints."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@patch("app.api.v1.endpoints.auth.UserService")
def test_login(mock_user_service_class, client):
    """Test user login endpoint."""
    # Create a mock instance with an async authenticate method
    mock_service = AsyncMock()
    mock_service.authenticate.return_value = MockUser(
        id=2,
        email="testuser@test.com",
        role="user",
        is_active=True,
        email_verified=True
    )
    # Make the mock class return our mock instance
    mock_user_service_class.return_value = mock_service
    
    # Login data
    login_data = {
        "username": "testuser@test.com",  # Using email as username
        "password": "testuser123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    
    # Verify the mock was called correctly
    mock_service.authenticate.assert_called_once()


@patch("app.services.user.service.UserService.get_current_user")
@patch("app.api.v1.endpoints.auth.UserService")
def test_refresh_token(mock_user_service_class, mock_get_current_user, client, user_headers):
    """Test token refresh endpoint."""
    # Mock the get_current_user dependency
    mock_get_current_user.return_value = MockUser(
        id=2,
        email="testuser@test.com",
        role="user"
    )
    
    # Create a mock instance with async methods
    mock_service = AsyncMock()
    mock_service.get.return_value = MockUser(
        id=2,
        email="testuser@test.com",
        role="user",
        is_active=True
    )
    # Make the mock class return our mock instance
    mock_user_service_class.return_value = mock_service
    
    response = client.post("/api/v1/auth/refresh", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@patch("app.services.user.service.UserService.get_current_user")
@patch("app.api.v1.endpoints.auth.token_service")
def test_logout(mock_token_service, mock_get_current_user, client, user_headers):
    """Test logout endpoint."""
    # Mock the get_current_user dependency
    mock_get_current_user.return_value = MockUser(
        id=2,
        email="testuser@test.com",
        role="user"
    )
    
    # Mock the blacklist_token method
    mock_token_service.blacklist_token = AsyncMock()
    
    response = client.post("/api/v1/auth/logout", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    # Verify the token was blacklisted
    mock_token_service.blacklist_token.assert_called_once()


@patch("app.api.v1.endpoints.auth.UserService")
@patch("app.api.v1.endpoints.auth.send_reset_password_email")
def test_password_reset_request(mock_send_email, mock_user_service_class, client):
    """Test password reset request endpoint."""
    # Create a mock instance with async methods
    mock_service = AsyncMock()
    mock_service.get_by_email.return_value = MockUser(
        id=2,
        email="testuser@test.com",
        is_active=True
    )
    # Make the mock class return our mock instance
    mock_user_service_class.return_value = mock_service
    
    request_data = {
        "email": "testuser@test.com"
    }
    
    response = client.post("/api/v1/auth/password-reset/request", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    # Verify the email was sent
    mock_send_email.assert_called_once()


@patch("app.api.v1.endpoints.auth.UserService")
def test_invalid_login(mock_user_service_class, client):
    """Test login with invalid credentials."""
    # Create a mock instance with an async authenticate method that returns None
    mock_service = AsyncMock()
    mock_service.authenticate.return_value = None
    # Make the mock class return our mock instance
    mock_user_service_class.return_value = mock_service
    
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data 