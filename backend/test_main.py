"""
Basic tests for the FastAPI application.
"""

from fastapi.testclient import TestClient
import pytest
import os
import base64
from cryptography.fernet import Fernet

from main import app, encrypt_api_key, decrypt_api_key

client = TestClient(app)

def test_read_main():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Anime Companion API"}

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()

def test_list_providers():
    """Test the API providers list endpoint."""
    response = client.get("/api/apikeys/providers")
    assert response.status_code == 200
    providers = response.json()["providers"]
    assert len(providers) > 0
    assert all(key in providers[0] for key in ["id", "name", "description"])

def test_encryption():
    """Test API key encryption and decryption."""
    # Set a test key
    test_key = Fernet.generate_key()
    os.environ["API_KEY_ENCRYPTION_KEY"] = test_key.decode()
    
    # Prepare test data
    original_key = "sk-test1234567890abcdef"
    
    # Initialize Fernet
    key_bytes = base64.urlsafe_b64encode(test_key.ljust(32)[:32])
    test_fernet = Fernet(key_bytes)
    
    # Encrypt
    encrypted = test_fernet.encrypt(original_key.encode()).decode()
    
    # Decrypt
    decrypted = test_fernet.decrypt(encrypted.encode()).decode()
    
    # Verify
    assert decrypted == original_key 