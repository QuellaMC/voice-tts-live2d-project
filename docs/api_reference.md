# API Reference

This document provides a comprehensive reference for all API endpoints available in the Voice TTS Live2D project.

## Base URLs

- **Main Application**: `http://localhost:8000/`
- **API (v1)**: `http://localhost:8000/api/v1/`
- **API Documentation**: `http://localhost:8000/api/docs`

## Authentication

Most API endpoints require authentication using JWT tokens. To authenticate:

1. Obtain a token by calling the `/api/v1/auth/login` endpoint
2. Include the token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

## Main Application Endpoints

### Root Endpoint

```
GET /
```

Returns a welcome message and links to the API and documentation.

**Response**:
```json
{
  "success": true,
  "message": "Welcome to the Voice TTS Live2D Project API",
  "data": {
    "api_url": "http://localhost:8000/api/v1/",
    "docs_url": "http://localhost:8000/api/docs"
  }
}
```

### Health Check

```
GET /health
```

Returns the health status of the application.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

## API v1 Endpoints

### Root Endpoint

```
GET /api/v1/
```

Returns a welcome message for the API.

**Response**:
```json
{
  "success": true,
  "message": "Welcome to the AI Anime Companion API",
  "data": null
}
```

### Health Check

```
GET /api/v1/health
```

Returns the health status of the API.

**Response**:
```json
{
  "success": true,
  "message": "Service is healthy",
  "data": {
    "status": "healthy",
    "version": "0.1.0"
  }
}
```

### Authentication

#### Login

```
POST /api/v1/auth/login
```

Authenticates a user and returns an access token.

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "[YOUR_ACCESS_TOKEN]",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token

```
POST /api/v1/auth/refresh
```

Refreshes an access token.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "access_token": "[YOUR_ACCESS_TOKEN]",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Logout

```
POST /api/v1/auth/logout
```

Invalidates the current access token.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

#### Password Reset Request

```
POST /api/v1/auth/password-reset/request
```

Requests a password reset link.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "success": true,
  "message": "If the email exists, a password reset link will be sent"
}
```

#### Reset Password

```
POST /api/v1/auth/password-reset/confirm
```

Resets password using a reset token.

**Request Body**:
```json
{
  "token": "reset-token",
  "new_password": "new-password123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

### User Management

#### Get Current User

```
GET /api/v1/users/me
```

Gets the current authenticated user's information.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": 1,
  "username": "user",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2023-05-01T00:00:00Z"
}
```

#### Update User

```
PUT /api/v1/users/me
```

Updates the current user's information.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "username": "updated_user",
  "email": "updated@example.com"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "updated_user",
  "email": "updated@example.com",
  "is_active": true,
  "created_at": "2023-05-01T00:00:00Z",
  "updated_at": "2023-05-02T00:00:00Z"
}
```

#### Change Password

```
PUT /api/v1/users/me/password
```

Changes the current user's password.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "current_password": "current-password",
  "new_password": "new-password123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

### Group Management

#### List Groups

```
GET /api/v1/groups/
```

Lists all available groups.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "admin",
      "description": "Administrator group with full permissions",
      "created_at": "2023-05-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "user",
      "description": "Standard user group",
      "created_at": "2023-05-01T00:00:00Z"
    }
  ],
  "total": 2
}
```

#### Create Group

```
POST /api/v1/groups/
```

Creates a new group (admin only).

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "name": "moderator",
  "description": "Moderator group with enhanced permissions"
}
```

**Response**:
```json
{
  "id": 3,
  "name": "moderator",
  "description": "Moderator group with enhanced permissions",
  "created_at": "2023-05-03T00:00:00Z"
}
```

#### Get Group

```
GET /api/v1/groups/{group_id}
```

Gets information about a specific group.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": 1,
  "name": "admin",
  "description": "Administrator group with full permissions",
  "created_at": "2023-05-01T00:00:00Z",
  "users": [
    {
      "id": 1,
      "username": "admin_user"
    }
  ]
}
```

#### Update Group

```
PUT /api/v1/groups/{group_id}
```

Updates a group (admin only).

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "description": "Updated group description"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "admin",
  "description": "Updated group description",
  "created_at": "2023-05-01T00:00:00Z",
  "updated_at": "2023-05-03T00:00:00Z"
}
```

#### Delete Group

```
DELETE /api/v1/groups/{group_id}
```

Deletes a group (admin only).

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Group deleted successfully"
}
```

#### Add User to Group

```
POST /api/v1/groups/{group_id}/users
```

Adds a user to a group (admin only).

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "user_id": 2
}
```

**Response**:
```json
{
  "success": true,
  "message": "User added to group successfully"
}
```

#### Remove User from Group

```
DELETE /api/v1/groups/{group_id}/users/{user_id}
```

Removes a user from a group (admin only).

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "User removed from group successfully"
}
```

### Knowledge Management

#### List Knowledge

```
GET /api/v1/knowledge/
```

Lists all knowledge entries.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)
- `topic` (optional): Filter by topic
- `tag` (optional): Filter by tag
- `concept` (optional): Filter by concept

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "topic": "Test Topic 1",
      "content": "Test content 1",
      "created_by": "testuser",
      "created_at": "2023-05-01T00:00:00Z",
      "updated_at": "2023-05-01T00:00:00Z"
    },
    {
      "id": 2,
      "topic": "Test Topic 2",
      "content": "Test content 2",
      "created_by": "testuser",
      "created_at": "2023-05-02T00:00:00Z",
      "updated_at": "2023-05-02T00:00:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

#### Create Knowledge

```
POST /api/v1/knowledge/
```

Creates a new knowledge entry.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "topic": "Test Knowledge",
  "content": "This is test content",
  "tags": ["test", "knowledge"]
}
```

**Response**:
```json
{
  "id": 1,
  "topic": "Test Knowledge",
  "content": "This is test content",
  "created_by": "testuser",
  "created_at": "2023-05-01T00:00:00Z",
  "updated_at": "2023-05-01T00:00:00Z",
  "tags": ["test", "knowledge"]
}
```

#### Get Knowledge

```
GET /api/v1/knowledge/{id}
```

Gets a specific knowledge entry.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": 1,
  "topic": "Test Knowledge",
  "content": "This is test content",
  "created_by": "testuser",
  "created_at": "2023-05-01T00:00:00Z",
  "updated_at": "2023-05-01T00:00:00Z",
  "tags": ["test", "knowledge"]
}
```

#### Update Knowledge

```
PUT /api/v1/knowledge/{id}
```

Updates a knowledge entry.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "topic": "Updated Knowledge",
  "content": "This is updated content",
  "tags": ["updated", "knowledge"]
}
```

**Response**:
```json
{
  "id": 1,
  "topic": "Updated Knowledge",
  "content": "This is updated content",
  "created_by": "testuser",
  "created_at": "2023-05-01T00:00:00Z",
  "updated_at": "2023-05-02T00:00:00Z",
  "tags": ["updated", "knowledge"]
}
```

#### Search Knowledge

```
POST /api/v1/knowledge/search
```

Searches for knowledge entries.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Query Parameters**:
- `query` (required): Search query
- `limit` (optional): Maximum number of results (default: 5)
- `min_similarity` (optional): Minimum similarity score (default: 0.7)
- `tags` (optional): Filter by tags
- `concepts` (optional): Filter by concepts

**Response**:
```json
[
  {
    "id": 1,
    "topic": "Test Topic 1",
    "content": "This is test content 1",
    "created_by": "testuser",
    "created_at": "2023-05-01T00:00:00Z",
    "updated_at": "2023-05-01T00:00:00Z",
    "score": 0.95
  },
  {
    "id": 2,
    "topic": "Test Topic 2",
    "content": "This is test content 2",
    "created_by": "testuser",
    "created_at": "2023-05-02T00:00:00Z",
    "updated_at": "2023-05-02T00:00:00Z",
    "score": 0.85
  }
]
```

#### Delete Knowledge

```
DELETE /api/v1/knowledge/{id}
```

Deletes a knowledge entry.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "status": "success",
  "message": "Knowledge entry deleted successfully"
}
```

#### Batch Create Knowledge

```
POST /api/v1/knowledge/batch
```

Creates multiple knowledge entries at once.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
[
  {
    "topic": "Batch Topic 1",
    "content": "Batch content 1",
    "tags": ["batch", "test"]
  },
  {
    "topic": "Batch Topic 2",
    "content": "Batch content 2",
    "tags": ["batch", "example"]
  }
]
```

**Response**:
```json
[
  {
    "id": 3,
    "topic": "Batch Topic 1",
    "content": "Batch content 1",
    "created_by": "testuser",
    "created_at": "2023-05-03T00:00:00Z",
    "updated_at": "2023-05-03T00:00:00Z",
    "tags": ["batch", "test"]
  },
  {
    "id": 4,
    "topic": "Batch Topic 2",
    "content": "Batch content 2",
    "created_by": "testuser",
    "created_at": "2023-05-03T00:00:00Z",
    "updated_at": "2023-05-03T00:00:00Z",
    "tags": ["batch", "example"]
  }
]
```

### Text-to-Speech

#### Synthesize Speech

```
POST /api/v1/tts/synthesize
```

Synthesizes speech from text.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Parameters**:
- `text` (required): Text to synthesize
- `voice_id` (required): Voice ID to use
- `options` (optional): Additional TTS options

**Response**:
```json
{
  "audio_url": "https://storage.example.com/audio/12345.mp3",
  "duration": 3.5,
  "file_size": 56320
}
```

#### List Voices

```
GET /api/v1/tts/voices
```

Lists all available TTS voices.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
[
  {
    "id": "voice-1",
    "name": "Female Voice 1",
    "gender": "female",
    "preview_url": "https://storage.example.com/previews/voice-1.mp3"
  },
  {
    "id": "voice-2",
    "name": "Male Voice 1",
    "gender": "male",
    "preview_url": "https://storage.example.com/previews/voice-2.mp3"
  }
]
```

#### Get Voice

```
GET /api/v1/tts/voices/{voice_id}
```

Gets details for a specific voice.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": "voice-1",
  "name": "Female Voice 1",
  "gender": "female",
  "preview_url": "https://storage.example.com/previews/voice-1.mp3",
  "description": "A natural-sounding female voice",
  "created_at": "2023-05-01T00:00:00Z"
}
```

#### Create Voice

```
POST /api/v1/tts/voices
```

Creates a new custom voice.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body (multipart/form-data)**:
- `voice_name` (required): Name for the new voice
- `samples` (required): Audio samples for voice training
- `description` (optional): Voice description

**Response**:
```json
{
  "id": "custom-voice-1",
  "name": "My Custom Voice",
  "status": "processing",
  "created_at": "2023-05-04T00:00:00Z"
}
```

#### Delete Voice

```
DELETE /api/v1/tts/voices/{voice_id}
```

Deletes a custom voice.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Voice deleted successfully"
}
```

#### Get TTS Settings

```
GET /api/v1/tts/settings
```

Gets TTS settings for the current user.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "default_voice_id": "voice-1",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "additional_settings": {
    "emphasis": 1.5
  }
}
```

#### Update TTS Settings

```
PUT /api/v1/tts/settings
```

Updates TTS settings for the current user.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "default_voice_id": "voice-2",
  "speed": 1.2,
  "pitch": 0.9,
  "volume": 1.1
}
```

**Response**:
```json
{
  "default_voice_id": "voice-2",
  "speed": 1.2,
  "pitch": 0.9,
  "volume": 1.1,
  "additional_settings": {
    "emphasis": 1.5
  }
}
```

### Live2D Integration

#### Animate Model

```
POST /api/v1/live2d/animate
```

Animates a Live2D model with motion data.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "model_id": "model-1",
  "motion_data": {
    "expression": "happy",
    "motion": "wave",
    "parameters": {
      "mouth_open": 0.5,
      "eye_open_left": 0.8,
      "eye_open_right": 0.8
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "animation_id": "anim-12345"
}
```

#### List Models

```
GET /api/v1/live2d/models
```

Lists all available Live2D models.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
[
  {
    "id": "model-1",
    "name": "Anime Character 1",
    "thumbnail_url": "https://storage.example.com/thumbnails/model-1.jpg"
  },
  {
    "id": "model-2",
    "name": "Anime Character 2",
    "thumbnail_url": "https://storage.example.com/thumbnails/model-2.jpg"
  }
]
```

#### Get Model

```
GET /api/v1/live2d/models/{model_id}
```

Gets details for a specific Live2D model.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": "model-1",
  "name": "Anime Character 1",
  "thumbnail_url": "https://storage.example.com/thumbnails/model-1.jpg",
  "model_url": "https://storage.example.com/models/model-1.model3.json",
  "supported_expressions": ["happy", "sad", "angry", "surprised"],
  "supported_motions": ["idle", "wave", "nod", "shake"],
  "created_at": "2023-05-01T00:00:00Z"
}
```

#### Upload Model

```
POST /api/v1/live2d/models
```

Uploads a new Live2D model.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body (multipart/form-data)**:
- `model_name` (required): Name for the model
- `model_file` (required): Live2D model file (zip archive)
- `thumbnail` (optional): Thumbnail image

**Response**:
```json
{
  "id": "model-3",
  "name": "My Custom Model",
  "thumbnail_url": "https://storage.example.com/thumbnails/model-3.jpg",
  "model_url": "https://storage.example.com/models/model-3.model3.json",
  "status": "processing",
  "created_at": "2023-05-04T00:00:00Z"
}
```

#### Delete Model

```
DELETE /api/v1/live2d/models/{model_id}
```

Deletes a Live2D model.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Model deleted successfully"
}
```

#### Get Live2D Settings

```
GET /api/v1/live2d/settings
```

Gets Live2D settings for the current user.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "default_model_id": "model-1",
  "motion_frequency": 0.5,
  "idle_animation": "breathing",
  "expression_intensity": 0.8
}
```

#### Update Live2D Settings

```
PUT /api/v1/live2d/settings
```

Updates Live2D settings for the current user.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "default_model_id": "model-2",
  "motion_frequency": 0.7,
  "idle_animation": "slight_movement"
}
```

**Response**:
```json
{
  "default_model_id": "model-2",
  "motion_frequency": 0.7,
  "idle_animation": "slight_movement",
  "expression_intensity": 0.8
}
```

### AI Companion

#### Chat with Companion

```
POST /api/v1/companion/chat
```

Sends a message to the AI companion and gets a response.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "message": "Hello, how are you today?",
  "companion_id": "companion-1",
  "conversation_id": "conv-12345"
}
```

**Response**:
```json
{
  "id": "msg-67890",
  "role": "assistant",
  "content": "Hello! I'm doing great today. How about you?",
  "companion_id": "companion-1",
  "conversation_id": "conv-12345",
  "created_at": "2023-05-04T12:34:56Z",
  "audio": {
    "url": "https://storage.example.com/audio/response-67890.mp3",
    "duration": 2.5
  },
  "animation": {
    "expression": "happy",
    "motion": "slight_nod"
  }
}
```

#### List Companions

```
GET /api/v1/companion/
```

Lists all companions available to the user.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
[
  {
    "id": "companion-1",
    "name": "Miku",
    "description": "A cheerful virtual companion",
    "thumbnail_url": "https://storage.example.com/thumbnails/companion-1.jpg",
    "created_at": "2023-05-01T00:00:00Z"
  },
  {
    "id": "companion-2",
    "name": "Haru",
    "description": "A calm and wise virtual companion",
    "thumbnail_url": "https://storage.example.com/thumbnails/companion-2.jpg",
    "created_at": "2023-05-02T00:00:00Z"
  }
]
```

#### Get Companion

```
GET /api/v1/companion/{companion_id}
```

Gets details for a specific companion.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "id": "companion-1",
  "name": "Miku",
  "description": "A cheerful virtual companion",
  "thumbnail_url": "https://storage.example.com/thumbnails/companion-1.jpg",
  "model_id": "model-1",
  "voice_id": "voice-1",
  "personality": "Cheerful and energetic",
  "knowledge_base_ids": [1, 2, 3],
  "created_at": "2023-05-01T00:00:00Z",
  "created_by": "user-123"
}
```

#### Create Companion

```
POST /api/v1/companion/
```

Creates a new companion.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "name": "New Companion",
  "description": "My custom companion",
  "model_id": "model-2",
  "voice_id": "voice-2",
  "personality": "Shy but friendly",
  "knowledge_base_ids": [4, 5]
}
```

**Response**:
```json
{
  "id": "companion-3",
  "name": "New Companion",
  "description": "My custom companion",
  "thumbnail_url": null,
  "model_id": "model-2",
  "voice_id": "voice-2",
  "personality": "Shy but friendly",
  "knowledge_base_ids": [4, 5],
  "created_at": "2023-05-04T12:34:56Z",
  "created_by": "user-123"
}
```

#### Update Companion

```
PUT /api/v1/companion/{companion_id}
```

Updates a companion.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "name": "Updated Companion",
  "description": "My updated companion description",
  "personality": "More outgoing and cheerful"
}
```

**Response**:
```json
{
  "id": "companion-3",
  "name": "Updated Companion",
  "description": "My updated companion description",
  "thumbnail_url": null,
  "model_id": "model-2",
  "voice_id": "voice-2",
  "personality": "More outgoing and cheerful",
  "knowledge_base_ids": [4, 5],
  "created_at": "2023-05-04T12:34:56Z",
  "updated_at": "2023-05-05T01:23:45Z",
  "created_by": "user-123"
}
```

#### Delete Companion

```
DELETE /api/v1/companion/{companion_id}
```

Deletes a companion.

**Headers**:
```
Authorization: Bearer <your_token>
```

**Response**:
```json
{
  "success": true,
  "message": "Companion deleted successfully"
}
```

## Interactive API Documentation

For a more interactive experience, you can use the Swagger UI documentation available at:

```
http://localhost:8000/api/docs
```

This provides a web-based interface where you can:
- Browse all available endpoints
- See request and response schemas
- Try out endpoints directly from the browser
- View authentication requirements

## Error Responses

All API endpoints return standard error responses in the following format:

```json
{
  "success": false,
  "error": "Error type",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

Common HTTP status codes:
- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Notes on Docker Environment

When running the application in Docker, you may need to restart the Docker container after making changes to the code. This can be done with:

```bash
docker-compose restart backend
```

This ensures that the changes are picked up by the server. 