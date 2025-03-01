"""Mock services for testing."""

import pytest
from unittest.mock import MagicMock
from typing import Dict, List, Any, Optional
from datetime import datetime


class MockUserService:
    """Mock user service for testing."""
    
    def __init__(self):
        """Initialize with some default users."""
        self.users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@test.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin123"
                "role": "admin",
                "is_active": True,
                "email_verified": True,
                "created_at": datetime.utcnow(),
                "last_login": None
            },
            {
                "id": 2,
                "username": "testuser",
                "email": "testuser@test.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "testuser123"
                "role": "user",
                "is_active": True,
                "email_verified": True,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
        ]
        self.next_id = 3
    
    async def authenticate(self, db, email: str, password: str):
        """Mock authenticate user."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        
        # In a real implementation, we would verify the password
        # For testing, we'll just check if the password is "testuser123" or "admin123"
        if password not in ["testuser123", "admin123"]:
            return None
            
        return user
    
    async def get_by_email(self, db, email: str):
        """Mock get user by email."""
        for user in self.users:
            if user["email"] == email:
                return user
        return None
    
    async def get(self, db, id: int):
        """Mock get user by ID."""
        for user in self.users:
            if user["id"] == id:
                return user
        return None
    
    async def create(self, db, obj_in):
        """Mock create user."""
        new_user = {
            "id": self.next_id,
            "username": obj_in.username,
            "email": obj_in.email,
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Mocked hash
            "role": "user",
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        self.users.append(new_user)
        self.next_id += 1
        return new_user
    
    async def update(self, db, db_obj, obj_in):
        """Mock update user."""
        for user in self.users:
            if user["id"] == db_obj["id"]:
                for key, value in obj_in.items():
                    if key != "id":  # Don't update ID
                        user[key] = value
                return user
        return None
    
    async def delete(self, db, id: int):
        """Mock delete user."""
        for i, user in enumerate(self.users):
            if user["id"] == id:
                return self.users.pop(i)
        return None
    
    async def get_current_user(self, token: str = None):
        """Mock get current user from token."""
        # For testing, we'll just return the test user
        return self.users[1]
    
    def get_password_hash(self, password: str):
        """Mock get password hash."""
        return "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # Mocked hash


class MockTTSService:
    """Mock TTS service for testing."""
    
    def __init__(self):
        """Initialize with some default voices."""
        self.voices = [
            {
                "voice_id": "voice-1",
                "name": "Test Voice 1",
                "description": "A test voice",
                "preview_url": "https://example.com/preview1.mp3"
            },
            {
                "voice_id": "voice-2",
                "name": "Test Voice 2",
                "description": "Another test voice",
                "preview_url": "https://example.com/preview2.mp3"
            }
        ]
        self.settings = {
            "default_voice": "voice-1",
            "speed": 1.0,
            "pitch": 1.0,
            "use_cache": True
        }
    
    async def synthesize(self, text: str, voice_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock synthesize speech."""
        return {
            "audio_url": "https://example.com/audio.mp3",
            "text": text,
            "voice_id": voice_id,
            "duration": 2.5
        }
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """Mock list voices."""
        return self.voices
    
    async def get_voice(self, voice_id: str) -> Dict[str, Any]:
        """Mock get voice."""
        for voice in self.voices:
            if voice["voice_id"] == voice_id:
                return voice
        return None
    
    async def create_voice(self, user_id: int, voice_name: str, samples: List[Any], description: Optional[str] = None) -> Dict[str, Any]:
        """Mock create voice."""
        new_voice = {
            "voice_id": f"voice-{len(self.voices) + 1}",
            "name": voice_name,
            "description": description or "Custom voice",
            "preview_url": "https://example.com/preview-custom.mp3"
        }
        self.voices.append(new_voice)
        return new_voice
    
    async def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        """Mock delete voice."""
        self.voices = [v for v in self.voices if v["voice_id"] != voice_id]
        return {"status": "success", "message": "Voice deleted successfully"}
    
    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Mock get settings."""
        return self.settings
    
    async def update_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Mock update settings."""
        self.settings.update(settings)
        return self.settings


class MockLive2DService:
    """Mock Live2D service for testing."""
    
    def __init__(self):
        """Initialize with some default models."""
        self.models = [
            {
                "model_id": "model-1",
                "name": "Test Model 1",
                "description": "A test model",
                "thumbnail_url": "https://example.com/thumbnail1.png"
            },
            {
                "model_id": "model-2",
                "name": "Test Model 2",
                "description": "Another test model",
                "thumbnail_url": "https://example.com/thumbnail2.png"
            }
        ]
        self.settings = {
            "default_model": "model-1",
            "physics_enabled": True,
            "auto_breathing": True,
            "idle_motion": "idle_01"
        }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Mock list models."""
        return self.models
    
    async def get_model(self, model_id: str) -> Dict[str, Any]:
        """Mock get model."""
        for model in self.models:
            if model["model_id"] == model_id:
                return model
        return None
    
    async def upload_model(self, user_id: int, model_name: str, model_file: Any, thumbnail: Optional[Any] = None) -> Dict[str, Any]:
        """Mock upload model."""
        new_model = {
            "model_id": f"model-{len(self.models) + 1}",
            "name": model_name,
            "description": "Custom model",
            "thumbnail_url": "https://example.com/thumbnail-custom.png"
        }
        self.models.append(new_model)
        return new_model
    
    async def delete_model(self, model_id: str) -> Dict[str, Any]:
        """Mock delete model."""
        self.models = [m for m in self.models if m["model_id"] != model_id]
        return {"status": "success", "message": "Model deleted successfully"}
    
    async def animate(self, model_id: str, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock animate."""
        return {
            "animation_data": {
                "model_id": model_id,
                "expression": motion_data.get("expression", "neutral"),
                "motion": motion_data.get("motion", "idle"),
                "parameters": motion_data.get("parameters", {})
            }
        }
    
    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Mock get settings."""
        return self.settings
    
    async def update_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Mock update settings."""
        self.settings.update(settings)
        return self.settings


class MockCompanionService:
    """Mock companion service for testing."""
    
    def __init__(self):
        """Initialize with some default companions."""
        self.companions = [
            {
                "id": 1,
                "user_id": 2,
                "name": "Test Companion 1",
                "description": "A test companion",
                "personality": "Friendly",
                "voice_id": "voice-1",
                "live2d_model": "model-1"
            }
        ]
        self.next_id = 2
    
    async def create_companion(self, user_id: int, companion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock create companion."""
        new_companion = {
            "id": self.next_id,
            "user_id": user_id,
            "name": companion_data.get("name", "New Companion"),
            "description": companion_data.get("description", ""),
            "personality": companion_data.get("personality", ""),
            "voice_id": companion_data.get("voice_id", ""),
            "live2d_model": companion_data.get("live2d_model", "")
        }
        self.companions.append(new_companion)
        self.next_id += 1
        return new_companion
    
    async def get_companion(self, companion_id: int) -> Dict[str, Any]:
        """Mock get companion."""
        for companion in self.companions:
            if companion["id"] == companion_id:
                return companion
        return None
    
    async def list_companions(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Mock list companions."""
        return [c for c in self.companions if c["user_id"] == user_id][skip:skip+limit]
    
    async def update_companion(self, companion_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock update companion."""
        for companion in self.companions:
            if companion["id"] == companion_id:
                companion.update(update_data)
                return companion
        return None
    
    async def delete_companion(self, companion_id: int) -> Dict[str, Any]:
        """Mock delete companion."""
        self.companions = [c for c in self.companions if c["id"] != companion_id]
        return {"status": "success", "message": "Companion deleted successfully"}
    
    async def chat_with_companion(self, companion_id: int, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Mock chat with companion."""
        return {
            "response": f"This is a mock response to: {message}",
            "companion_id": companion_id,
            "audio_url": "https://example.com/response-audio.mp3"
        }


class MockEmbeddingsService:
    """Mock embeddings service for testing."""
    
    def __init__(self):
        """Initialize with default settings."""
        self.embeddings = {}
    
    async def get_embedding(self, text: str) -> List[float]:
        """Mock get embedding."""
        # Return a fixed-size embedding vector (e.g., 384 dimensions)
        return [0.1] * 384
    
    async def search_by_text(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Mock search by text."""
        # Return mock search results
        return [
            {"id": 1, "score": 0.95, "content": "This is a test result 1"},
            {"id": 2, "score": 0.85, "content": "This is a test result 2"},
            {"id": 3, "score": 0.75, "content": "This is a test result 3"}
        ][:limit]
    
    async def add_embedding(self, text_id: int, text: str, embedding: Optional[List[float]] = None) -> None:
        """Mock add embedding."""
        if embedding is None:
            embedding = await self.get_embedding(text)
        self.embeddings[text_id] = embedding
    
    async def delete_embedding(self, text_id: int) -> None:
        """Mock delete embedding."""
        if text_id in self.embeddings:
            del self.embeddings[text_id]


@pytest.fixture
def mock_user_service(monkeypatch):
    """Fixture to mock user service."""
    mock_service = MockUserService()
    monkeypatch.setattr("app.services.user.UserService", lambda: mock_service)
    return mock_service


@pytest.fixture
def mock_tts_service(monkeypatch):
    """Fixture to mock TTS service."""
    mock_service = MockTTSService()
    monkeypatch.setattr("app.services.tts.tts_service", mock_service)
    return mock_service


@pytest.fixture
def mock_live2d_service(monkeypatch):
    """Fixture to mock Live2D service."""
    mock_service = MockLive2DService()
    monkeypatch.setattr("app.services.live2d.live2d_service", mock_service)
    return mock_service


@pytest.fixture
def mock_companion_service(monkeypatch):
    """Fixture to mock companion service."""
    mock_service = MockCompanionService()
    monkeypatch.setattr("app.services.companion.companion_service", mock_service)
    return mock_service


@pytest.fixture
def mock_embeddings_service(monkeypatch):
    """Fixture to mock embeddings service."""
    mock_service = MockEmbeddingsService()
    monkeypatch.setattr("app.services.knowledge.embeddings_service", mock_service)
    return mock_service


@pytest.fixture
def mock_openai(monkeypatch):
    """Fixture to mock OpenAI API."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a mock response from OpenAI."
    
    mock_create = MagicMock(return_value=mock_response)
    monkeypatch.setattr("openai.ChatCompletion.create", mock_create)
    return mock_create 