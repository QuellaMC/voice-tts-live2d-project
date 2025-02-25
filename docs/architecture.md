# System Architecture

This document outlines the architecture of the AI Anime Companion project.

## Overview

The system is built with a client-server architecture where:
- The **frontend** provides the user interface with Live2D rendering and chat functionality
- The **backend** handles AI processing, voice synthesis, and data management

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client (Web Browser)                       │
└───────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│                                                                 │
│  ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │  Chat Interface │  │ Live2D Renderer │  │ Audio Playback  │   │
│  └─────────────────┘  └────────────────┘  └─────────────────┘   │
│                                                                 │
└────────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                      │
│                                                                │
│  ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │  LLM Service    │  │  TTS Service   │  │  RVC Service    │  │
│  └─────────────────┘  └────────────────┘  └─────────────────┘  │
│                                                                │
│  ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │ User Manager    │  │ Space Manager  │  │ Model Manager   │  │
│  └─────────────────┘  └────────────────┘  └─────────────────┘  │
│                                                                │
│  ┌─────────────────┐                                           │
│  │ API Key Manager │                                           │
│  └─────────────────┘                                           │
│                                                                │
└──────────────┬───────────────────────────────────┬─────────────┘
               │                                   │
               ▼                                   ▼
┌─────────────────────────────┐      ┌──────────────────────────┐
│       Database Storage      │      │      External APIs        │
│  (User Data, Spaces, Chats) │      │  (OpenAI, ElevenLabs)     │
└─────────────────────────────┘      └──────────────────────────┘
```

## Component Details

### Frontend Components

1. **Chat Interface**
   - Displays conversation history
   - Accepts user input (text and audio)
   - Shows AI responses

2. **Live2D Renderer**
   - Renders Live2D model
   - Controls animations based on voice and emotion
   - Handles lip sync with audio

3. **Audio Playback**
   - Manages streaming audio from the backend
   - Controls playback of synthesized voice
   - Handles audio queuing and interruptions

### Backend Components

1. **LLM Service**
   - Interfaces with LLM APIs (OpenAI, Anthropic, etc.)
   - Manages context and conversation history
   - Integrates with knowledge base for custom data
   - Supports custom API endpoints configuration
   - Uses API Key Manager for authentication

2. **TTS Service**
   - Connects to Text-to-Speech providers
   - Generates speech from AI responses
   - Manages voice settings and configurations
   - Supports custom API endpoints
   - Uses API Key Manager for authentication

3. **RVC Service**
   - Processes TTS output through voice conversion
   - Applies character voice profiles
   - Manages voice model selection and parameters

4. **User Manager**
   - Handles user authentication and profiles
   - Manages user preferences and settings
   - Stores user-specific configurations
   - Manages user-specific API keys

5. **Space Manager**
   - Creates and manages AI companion spaces
   - Stores space-specific settings (personality, knowledge, etc.)
   - Handles space sharing and permissions
   - Associates API configurations with spaces

6. **Model Manager**
   - Manages Live2D model resources
   - Handles voice model configurations
   - Tracks model usage and permissions

7. **API Key Manager**
   - Stores and manages API keys for various services
   - Supports admin-managed API key pool
   - Handles user-provided API keys
   - Provides API key rotation and validation
   - Controls access to shared API keys
   - Manages custom API endpoints
   - **Key Features**:
     - Fernet symmetric encryption for API key storage
     - Per-provider custom endpoints configuration
     - Automatic API key validation with providers
     - Usage tracking and statistics
     - Key rotation mechanisms
     - Hierarchical access (admin/user/default)
     - Role-based access control for key management
   - **Implementation Details**:
     - Uses `cryptography.fernet` for key encryption/decryption
     - Encryption key stored in `API_KEY_ENCRYPTION_KEY` environment variable
     - Key validation logic per provider (`verify_api_key` function)
     - Three-tier priority system for key retrieval:
       1. User-specific keys (if available)
       2. Admin pool keys (if available)
       3. Default environment variables (fallback)

## Data Flow

1. **User Request Flow**
   - User sends message (text or voice)
   - Frontend sends request to backend API
   - Backend retrieves appropriate API keys (user-specific or from pool)
   - Backend processes request through LLM
   - Response is generated and sent to TTS
   - TTS output is processed through RVC
   - Audio is streamed back to frontend
   - Live2D animation is synced with audio

2. **Space Configuration Flow**
   - User creates/edits a space
   - Updates personality settings, knowledge base, model selection
   - Configures API providers and endpoints
   - Adds user-specific API keys if needed
   - Configuration is saved to database
   - Space is loaded with specified settings when accessed

3. **API Key Management Flow**
   - Admin adds API keys to the shared pool
   - System validates API keys on addition
   - Users can provide their own API keys
   - API keys are securely stored and encrypted
   - System uses appropriate keys based on availability and user settings

## API Endpoints

### Authentication
- `/api/auth/register` - User registration
- `/api/auth/login` - User login
- `/api/auth/refresh` - Refresh authentication token

### Conversation
- `/api/chat` - WebSocket endpoint for real-time chat
- `/api/chat/history` - Get conversation history

### Voice
- `/api/voice/stream` - Stream synthesized voice audio
- `/api/voice/models` - List available voice models
- `/api/voice/settings` - Update voice settings

### Live2D
- `/api/live2d/models` - List available Live2D models
- `/api/live2d/settings` - Update Live2D settings

### Spaces
- `/api/spaces` - List user spaces
- `/api/spaces/{id}` - Get specific space
- `/api/spaces/create` - Create new space
- `/api/spaces/{id}/update` - Update space settings
- `/api/spaces/{id}/knowledge` - Manage knowledge base

### API Keys
- `/api/apikeys` - Manage user API keys
- `/api/apikeys/validate` - Validate an API key
- `/api/apikeys/providers` - List supported API providers
- `/api/admin/apikeys` - Admin management of API key pool

## Security Considerations

- API keys stored securely in encrypted format
- User-specific API keys isolated from other users
- User authentication with JWT
  - **JWT Implementation**:
    - Token generation and validation in `dependencies.py`
    - Role-based authorization (`get_current_user` and `get_current_admin` functions)
    - Token payload contains user ID, role, and expiration time
    - Configurable token lifetime and algorithm
    - JWT secret controlled via environment variable
  - **Authentication Flow**:
    1. User logs in with username/password
    2. Server validates credentials and generates JWT
    3. Client stores JWT and sends it with subsequent requests
    4. Server validates JWT with each request to determine user identity and permissions
- HTTPS for all communications
- Rate limiting on API endpoints
- Input validation and sanitization
- Proper error handling
- API key validation before use
  - Format validation for known providers (e.g., OpenAI keys start with "sk-")
  - Optional live validation with provider APIs
  - Configurable validation via `VERIFY_API_KEYS` environment variable

## Performance Considerations

- WebSocket for real-time communication
- Audio streaming for immediate playback
- Caching of frequently used responses
- Optimized Live2D rendering
- Background processing for intensive tasks
- Scalable architecture for high user loads
- API key pooling to optimize usage and costs 