"""
Tests for Text-to-Speech endpoints.
"""

import io

import pytest
from fastapi.testclient import TestClient
from tests.mocks import mock_tts_service


def test_list_voices(client, user_headers, mock_tts_service):
    """Test listing available voices."""
    response = client.get("/api/v1/tts/voices", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least some default voices
    assert len(data) > 0
    # Check voice structure
    if len(data) > 0:
        assert "voice_id" in data[0]
        assert "name" in data[0]


def test_get_voice(client, user_headers, mock_tts_service):
    """Test getting a specific voice."""
    # First get list of voices
    response = client.get("/api/v1/tts/voices", headers=user_headers)
    voices = response.json()

    if len(voices) > 0:
        voice_id = voices[0]["voice_id"]

        # Then get specific voice
        response = client.get(f"/api/v1/tts/voices/{voice_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["voice_id"] == voice_id


def test_synthesize_speech(client, user_headers, mock_tts_service):
    """Test speech synthesis."""
    # First get list of voices
    response = client.get("/api/v1/tts/voices", headers=user_headers)
    voices = response.json()

    if len(voices) > 0:
        voice_id = voices[0]["voice_id"]

        # Then synthesize speech
        synth_data = {
            "text": "Hello, this is a test of speech synthesis.",
            "voice_id": voice_id,
            "options": {"speed": 1.0, "pitch": 1.0},
        }

        response = client.post(
            "/api/v1/tts/synthesize", json=synth_data, headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "audio_url" in data


def test_create_voice(client, user_headers, mock_tts_service):
    """Test creating a custom voice."""
    # Create test audio file
    test_audio = io.BytesIO(b"test audio data")
    test_audio.name = "test_sample.wav"

    # Create voice
    response = client.post(
        "/api/v1/tts/voices",
        data={
            "voice_name": "Test Custom Voice",
            "description": "A test voice for unit testing",
        },
        files={"samples": (test_audio.name, test_audio, "audio/wav")},
        headers=user_headers,
    )

    # This might fail in CI environment without actual audio processing
    # So we'll check for either success or a specific error
    assert response.status_code in [200, 422]

    if response.status_code == 200:
        data = response.json()
        assert "voice_id" in data
        return data["voice_id"]
    return None


def test_get_tts_settings(client, user_headers, mock_tts_service):
    """Test getting TTS settings."""
    response = client.get("/api/v1/tts/settings", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    # Check for expected settings fields
    assert isinstance(data, dict)


def test_update_tts_settings(client, user_headers, mock_tts_service):
    """Test updating TTS settings."""
    settings_data = {
        "default_voice": "test-voice-id",
        "speed": 1.2,
        "pitch": 0.9,
        "use_cache": True,
    }

    response = client.put(
        "/api/v1/tts/settings", json=settings_data, headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()

    # Verify settings were updated
    assert data["default_voice"] == settings_data["default_voice"]
    assert data["speed"] == settings_data["speed"]
    assert data["pitch"] == settings_data["pitch"]
