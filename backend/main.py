from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
import json
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize encryption for API keys
API_KEY_ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY")
fernet = None
if API_KEY_ENCRYPTION_KEY:
    try:
        # Properly prepare the key for Fernet (must be 32 url-safe base64-encoded bytes)
        # Convert string to bytes if necessary
        if isinstance(API_KEY_ENCRYPTION_KEY, str):
            API_KEY_ENCRYPTION_KEY = API_KEY_ENCRYPTION_KEY.encode()
            
        # Use proper key derivation
        key_bytes = base64.urlsafe_b64encode(API_KEY_ENCRYPTION_KEY.ljust(32)[:32])
        fernet = Fernet(key_bytes)
        logger.info("API key encryption initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API key encryption: {str(e)}")
        logger.warning("API keys will not be encrypted. Generate a valid key with Fernet.generate_key()")
else:
    logger.warning("API_KEY_ENCRYPTION_KEY not set, API keys will not be encrypted")

# Initialize FastAPI app
app = FastAPI(
    title="AI Anime Companion API",
    description="Backend API for the AI Anime Companion project",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions for API key management
def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure storage."""
    if not fernet:
        logger.warning("Encryption not available, storing API key unencrypted")
        return api_key  # No encryption if not configured
    try:
        return fernet.encrypt(api_key.encode()).decode()
    except Exception as e:
        logger.error(f"Failed to encrypt API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to securely store API key")

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key for use."""
    if not fernet:
        logger.warning("Encryption not available, using API key as-is")
        return encrypted_key  # No decryption if not configured
    try:
        return fernet.decrypt(encrypted_key.encode()).decode()
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API key")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Anime Companion API"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

# API Providers list
@app.get("/api/apikeys/providers")
async def list_providers():
    """List all supported API providers."""
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI", "description": "GPT models provider"},
            {"id": "anthropic", "name": "Anthropic", "description": "Claude models provider"},
            {"id": "elevenlabs", "name": "ElevenLabs", "description": "Voice synthesis provider"},
            {"id": "azure", "name": "Azure TTS", "description": "Microsoft TTS provider"},
        ]
    }

# Run the FastAPI app if executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True) 