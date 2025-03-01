# Setup Guide

This guide will help you set up the AI Anime Companion project on your local machine.

## Prerequisites

- Python 3.9+ 
- Node.js 18+ and npm/yarn
- Docker (optional, for containerization)
- GPU (recommended for faster processing)
- API keys for LLM and TTS services

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/voice-tts-live2d-project.git
cd voice-tts-live2d-project
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file and edit it with your own settings:

```bash
cp .env.example .env
# Now edit .env with your preferred text editor
```

The `.env` file should contain the following settings (already present in the example file):

```
# LLM API Configuration
# Default API keys (used as fallback or for admin-managed pool)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
# Add others as needed

# Custom API endpoints (optional)
OPENAI_API_BASE_URL=https://api.openai.com
ANTHROPIC_API_BASE_URL=https://api.anthropic.com
# Add others as needed

# TTS Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=your_azure_region

# API Key Management
API_KEY_ENCRYPTION_KEY=your_secure_encryption_key
VERIFY_API_KEYS=true  # Whether to verify API keys with providers

# Authentication
JWT_SECRET=your_secure_jwt_secret_key  # For user authentication
JWT_ALGORITHM=HS256  # Default algorithm

# Database Configuration
DATABASE_URL=your_database_connection_string

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install  # or: yarn install
```

Create a `.env.local` file in the `frontend` directory:

```bash
# Create and edit .env.local with your preferred text editor
```

The `.env.local` file should contain:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Model Setup

#### Live2D Models
- Place your Live2D models in the `models/live2d` directory
- Supported formats: `.model3.json` files with related textures and motions

#### RVC Voice Models
- Place your RVC voice models in the `models/rvc` directory
- Models should include the necessary configuration files

#### LLM (Local Models - Optional)
- If using local LLMs, place model files in `models/llm`
- Configure in the backend settings

### 5. API Key Management Setup

The system supports both user-provided API keys and an admin-managed API key pool:

#### Admin API Key Pool
- Admin can add API keys through the admin interface
- Keys in the pool can be shared among users without their own keys
- Set up initial admin account in the database:

```bash
# Using provided script (requires running backend server)
cd scripts
python create_admin.py --username admin --password secure_password
```

#### JWT Authentication Details

JWT (JSON Web Tokens) is used for secure authentication. The system uses the following JWT configuration:

- **Token Structure**: JWT tokens contain user ID, role, and expiration time
- **Token Lifetime**: Default is 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in dependencies.py)
- **Algorithm**: HS256 (configurable via `JWT_ALGORITHM` environment variable)
- **Secret Key**: Set via the `JWT_SECRET` environment variable

To create an admin account with a valid JWT token:

```bash
# Generate a token with admin privileges
cd scripts
python create_admin.py --username admin --password secure_password --jwt-secret your_secret_key
```

The script will output a JWT token that can be used for authentication with admin privileges. This token can be used in API requests with the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### API Key Management API Endpoints

The system provides the following endpoints for API key management:

- **List Providers**: `GET /api/apikeys/providers` - Lists all supported API providers
- **Validate Key**: `POST /api/apikeys/validate` - Validates an API key with the provider
- **User Keys**: `GET /api/apikeys` - Gets a user's stored API keys (redacted)
- **Save Key**: `POST /api/apikeys` - Saves a user's API key
- **Delete Key**: `DELETE /api/apikeys/{provider}` - Deletes a user's API key

Admin-only endpoints:
- **List Pool**: `GET /api/admin/apikeys` - Lists all API keys in the admin pool
- **Add to Pool**: `POST /api/admin/apikeys` - Adds an API key to the admin pool
- **Delete from Pool**: `DELETE /api/admin/apikeys/{key_id}` - Deletes an API key from the pool

Example of adding a user API key:

```bash
curl -X POST http://localhost:8000/api/apikeys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "api_key": "sk-your-key", "custom_endpoint": "https://api.custom-openai.com"}'
```

Example of validating an API key:

```bash
curl -X POST http://localhost:8000/api/apikeys/validate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "api_key": "sk-your-key"}'
```

#### API Key Security

API keys are encrypted before storage using the Fernet symmetric encryption algorithm:

1. The `API_KEY_ENCRYPTION_KEY` environment variable provides the encryption key
2. Keys are only decrypted when needed for API calls
3. Redacted versions are shown in the UI and API responses
4. If the encryption key is not set, the system will log warnings about unencrypted storage

#### User-Specific API Keys
- Users can provide their own API keys in their account settings
- These keys take precedence over the shared pool
- Keys are encrypted before storage and only decrypted when needed

#### API Key Validation
- The system can validate API keys with providers before accepting them
- Control this with the `VERIFY_API_KEYS` environment variable
- Validation adds security but increases API usage

## Running the Application

### Development Mode

1. Start the backend server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev  # or: yarn dev
```

3. Access the application at: http://localhost:3000

### Using Docker (Optional)

Before starting the Docker containers, make sure to copy and configure the environment file:

```bash
# Copy environment file
cp .env.example .env

# Edit the file with your preferred text editor to add your API keys and settings
```

Also create a `.env.local` file in the frontend directory:

```bash
# Create frontend/.env.local file
mkdir -p frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

Then start the Docker containers:

```bash
docker-compose up
```

This will start all the services defined in the `docker-compose.yml` file.

### 4. Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### 5. Development Workflow

When making changes to the code while the Docker containers are running, you may need to restart the containers for the changes to take effect:

```bash
# Restart a specific service
docker-compose restart backend

# Or restart all services
docker-compose restart
```

For frontend changes, the development server should automatically reload when files are changed.

For backend changes, you may need to restart the backend service:

```bash
docker-compose restart backend
```

This is particularly important for changes to:
- Route definitions
- Dependency injections
- Service implementations
- Database models

## Configuration Options

### LLM Settings
- Model selection (GPT-4, Claude, Mistral, etc.)
- Temperature and response parameters
- System prompt templates
- Custom API endpoints
- API key preferences (user key or shared pool)

### Voice Conversion Settings
- RVC model selection
- Voice parameters (pitch, speed, etc.)
- Output audio quality
- Custom TTS API endpoints

### Live2D Settings
- Model selection
- Animation parameters
- Expression mappings

### API Key Settings
- User API key management
- Custom API endpoint configuration
- API key validation options
- API key usage statistics (admin only)

### Authentication Settings
- JWT token configuration
- User roles and permissions
- Session management

## Troubleshooting

- **API Connection Issues**: Verify API keys and network connectivity
- **Model Loading Errors**: Check model format compatibility
- **Performance Issues**: Consider using a GPU for faster processing
- **Audio Playback Problems**: Check browser audio settings and permissions
- **API Key Validation Failures**: Ensure keys have correct permissions and quotas
- **Authentication Issues**: Check JWT secret and token configuration

## Additional Resources

- [Live2D Cubism SDK Documentation](https://docs.live2d.com/)
- [RVC (Retrieval-based Voice Conversion) Repository](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)