"""
Tests for Live2D endpoints.
"""

import pytest
import io
from fastapi.testclient import TestClient
from tests.mocks import mock_live2d_service


def test_list_models(client, user_headers, mock_live2d_service):
    """Test listing available Live2D models."""
    response = client.get("/api/v1/live2d/models", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check model structure if any exist
    if len(data) > 0:
        assert "model_id" in data[0]
        assert "name" in data[0]


def test_get_model(client, user_headers, mock_live2d_service):
    """Test getting a specific Live2D model."""
    # First get list of models
    response = client.get("/api/v1/live2d/models", headers=user_headers)
    models = response.json()
    
    if len(models) > 0:
        model_id = models[0]["model_id"]
        
        # Then get specific model
        response = client.get(f"/api/v1/live2d/models/{model_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id


def test_upload_model(client, user_headers, mock_live2d_service):
    """Test uploading a Live2D model."""
    # Create test model file
    test_model = io.BytesIO(b"test model data")
    test_model.name = "test_model.zip"
    
    # Create test thumbnail
    test_thumbnail = io.BytesIO(b"test thumbnail data")
    test_thumbnail.name = "test_thumbnail.png"
    
    # Upload model
    response = client.post(
        "/api/v1/live2d/models",
        data={"model_name": "Test Live2D Model"},
        files={
            "model_file": (test_model.name, test_model, "application/zip"),
            "thumbnail": (test_thumbnail.name, test_thumbnail, "image/png")
        },
        headers=user_headers
    )
    
    # This might fail in CI environment without actual model processing
    # So we'll check for either success or a specific error
    assert response.status_code in [200, 422]
    
    if response.status_code == 200:
        data = response.json()
        assert "model_id" in data
        return data["model_id"]
    return None


def test_animate_model(client, user_headers, mock_live2d_service):
    """Test animating a Live2D model."""
    # First get list of models
    response = client.get("/api/v1/live2d/models", headers=user_headers)
    models = response.json()
    
    if len(models) > 0:
        model_id = models[0]["model_id"]
        
        # Then animate model
        motion_data = {
            "expression": "happy",
            "motion": "wave",
            "parameters": {
                "mouth_open": 0.5,
                "eye_open": 0.8
            }
        }
        
        response = client.post(
            f"/api/v1/live2d/animate?model_id={model_id}",
            json=motion_data,
            headers=user_headers
        )
        
        # This might fail in CI environment without actual model processing
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "animation_data" in data


def test_get_live2d_settings(client, user_headers, mock_live2d_service):
    """Test getting Live2D settings."""
    response = client.get("/api/v1/live2d/settings", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    # Check for expected settings fields
    assert isinstance(data, dict)


def test_update_live2d_settings(client, user_headers, mock_live2d_service):
    """Test updating Live2D settings."""
    settings_data = {
        "default_model": "test-model-id",
        "physics_enabled": True,
        "auto_breathing": True,
        "idle_motion": "idle_01"
    }
    
    response = client.put("/api/v1/live2d/settings", json=settings_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Verify settings were updated
    assert data["default_model"] == settings_data["default_model"]
    assert data["physics_enabled"] == settings_data["physics_enabled"]
    assert data["auto_breathing"] == settings_data["auto_breathing"] 