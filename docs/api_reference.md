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
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MTY...",
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
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MTY...",
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

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "topic": "Test Topic 1",
      "content": "Test content 1",
      "created_by": "testuser",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "topic": "Test Topic 2",
      "content": "Test content 2",
      "created_by": "testuser",
      "created_at": "2023-01-02T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "pages": 1
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
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
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
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
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
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z",
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

**Response**:
```json
[
  {
    "id": 1,
    "topic": "Test Topic 1",
    "content": "This is test content 1",
    "created_by": "testuser",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "score": 0.95
  },
  {
    "id": 2,
    "topic": "Test Topic 2",
    "content": "This is test content 2",
    "created_by": "testuser",
    "created_at": "2023-01-02T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z",
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