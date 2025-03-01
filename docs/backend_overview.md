# Backend Overview

## Introduction

The backend API is built using FastAPI and is designed to be modular and scalable to meet large project standards. This documentation provides an overview of the architecture, file structure, and design decisions implemented in the project.

## File Structure

- **main.py**: Initializes the FastAPI application, sets up middleware (CORS), logging, environment variables, encryption, and includes the API routers. Also defines the main application endpoints.
- **config.py**: Handles configuration by loading environment variables using dotenv, initializing shared resources (e.g., Fernet for encryption), and providing a central point for configuration management.
- **app/api/v1/endpoints/**
  - **root.py**: Contains API root endpoints ("/api/v1/" and "/api/v1/health") to provide basic API status and welcome messages.
  - **auth.py**: Contains authentication endpoints for login, logout, token refresh, and password reset.
  - **knowledge.py**: Contains the knowledge management endpoints for creating, reading, updating, and deleting knowledge entries.
  - **users.py**: Contains user management endpoints.
  - **groups.py**: Contains group management endpoints.
  - **tts.py**: Contains text-to-speech endpoints.
  - **live2d.py**: Contains Live2D model management endpoints.
  - **companion.py**: Contains AI companion management endpoints.
- **app/services/**
  - **base/**: Contains base service classes and interfaces for common CRUD operations.
  - **auth/**: Contains authentication-related services.
  - **user/**: Contains user management services.
  - **knowledge/**: Contains knowledge management services.
  - **permissions/**: Contains permission management services.
  - **companion/**: Contains AI companion services.
  - **live2d/**: Contains Live2D model management services.
  - **tts/**: Contains text-to-speech services.
- **app/models/**: Contains the SQLAlchemy models for the database.
- **app/schemas/**: Contains Pydantic models for request and response validation.
- **app/core/**: Contains core functionality like configuration, security, and monitoring.
- **app/database/**: Contains database session management.
- **tests/**: Contains tests for the application.

## Endpoint Structure

The application has two levels of endpoints:

1. **Main Application Endpoints**: Defined in `main.py`
   - `/`: Welcome page with links to API and documentation
   - `/health`: Health check endpoint

2. **API v1 Endpoints**: Defined in `app/api/v1/endpoints/`
   - `/api/v1/`: API welcome page
   - `/api/v1/health`: API health check endpoint
   - `/api/v1/auth/*`: Authentication endpoints
   - `/api/v1/knowledge/*`: Knowledge management endpoints
   - `/api/v1/users/*`: User management endpoints
   - `/api/v1/groups/*`: Group management endpoints
   - `/api/v1/tts/*`: Text-to-speech endpoints
   - `/api/v1/live2d/*`: Live2D model management endpoints
   - `/api/v1/companion/*`: AI companion management endpoints

## Routing and Modularity

The backend leverages FastAPI's router mechanism to split endpoints into modular components. This design supports community best practices by:

- Separating core API endpoints into dedicated routers (e.g., root and knowledge routers).
- Making future extensions easier by isolating business logic within services and routing mechanisms.

## Configuration and Security

- **Configuration Management**: The use of a dedicated config.py file centralizes environment variable loading and shared configurations. This reduces redundancy and improves maintainability.
- **Encryption**: API key encryption is handled by initializing a Fernet cipher from configuration. This ensures that sensitive data is secured if proper keys are provided.
- **CORS**: Configured in main.py. Although it is set to allow all origins for now, it is recommended to restrict access in a production environment.

## Extensibility and Best Practices

- **Modularization**: The clear separation of API endpoints (routers), business logic (services), and configuration (config) makes the codebase highly extendable and maintainable.
- **Scalability**: New features can be added by creating additional routers and services without cluttering the main application file.
- **Security**: Proper logging, error handling, and environment-based configuration ensure a robust baseline for security.

This overview should serve as a guide for developers to understand the backend architecture and follow the design principles laid out for scalability and maintainability in large-scale projects. 