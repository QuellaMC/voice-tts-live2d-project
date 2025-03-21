# AI Anime Companion (Voice-TTS-Live2D)

An interactive AI-powered anime companion with custom voice synthesis and Live2D animations.

> **⚠️ Note:** This project is still in active development and not yet production-ready. Features may be incomplete or subject to change.
> 
> This project represents my first attempt at learning how to build a fullstack application with generative AI technologies.

## Features

- **Intelligent Conversations**: Powered by LLMs (GPT/Claude/Mistral) with custom knowledge base integration
- **Voice Synthesis**: Text-to-Speech with anime voice conversion using RVC
- **Live2D Animation**: Interactive anime character visualization with lip sync and expressions
- **Customizable Spaces**: Create different AI companions with unique personalities, knowledge, and appearances
- **User-friendly Interface**: Seamless chat and interaction experience
- **Flexible API Management**: Use your own API keys or access admin-managed key pools with custom endpoints

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-tts-live2d-project.git
   cd voice-tts-live2d-project
   ```

2. **Set up environment files**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Create frontend environment file
   mkdir -p frontend
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
   ```
   
   Edit the `.env` file to add your API keys and custom endpoints.

3. **Start the development environment**
   ```bash
   docker-compose up
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
   
   This step creates all necessary database tables and relationships. It's required for first-time setup or after pulling updates with database changes.

5. **Create an admin account**
   ```bash
   # Create admin account from within the backend container
   docker-compose exec backend python scripts/create_admin.py --username admin --password secure_password
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Development

### Frontend
- React/Next.js for UI components
- Live2D Cubism SDK for character rendering
- WebSockets for real-time communication

### Backend
- FastAPI (Python) for backend processing
- LLM integration (OpenAI, Anthropic, or local models)
- TTS services (ElevenLabs, Microsoft Azure, etc.)
- RVC for voice conversion
- PostgreSQL for data storage
- Redis for caching and session management
- Secure API key management and encryption

## Project Structure

```
voice-tts-live2d-project/
├── frontend/               # React/Next.js frontend application
├── backend/                # FastAPI backend server
├── docs/                   # Documentation
├── models/                 # Pre-trained models and configurations
│   ├── live2d/            # Live2D model files
│   ├── rvc/               # RVC voice models
│   └── llm/               # Local LLM configurations (if applicable)
└── scripts/               # Utility scripts
```

## Documentation

For detailed Docker setup instructions, see the [Docker Setup Guide](./docs/docker-setup.md).

For architecture and design details, see the [Architecture Documentation](./docs/architecture.md).

For the development roadmap, see the [Roadmap](./docs/roadmap.md).

For a comprehensive API reference, see the [API Reference](./docs/api_reference.md).

## API Endpoints

The application provides several endpoints:

- **Main Application Endpoints**:
  - `http://localhost:8000/` - Welcome page with links to API and documentation
  - `http://localhost:8000/health` - Health check endpoint

- **API v1 Endpoints**:
  - `http://localhost:8000/api/v1/` - API welcome page
  - `http://localhost:8000/api/v1/health` - API health check endpoint
  - `http://localhost:8000/api/v1/auth/*` - Authentication endpoints
  - `http://localhost:8000/api/v1/knowledge/*` - Knowledge management endpoints

- **API Documentation**:
  - `http://localhost:8000/api/docs` - Interactive Swagger UI documentation

## Testing

The project includes a comprehensive testing framework for the backend:

### Running Tests

1. **Run tests in Docker**
   ```bash
   chmod +x run_tests_docker.sh
   ./run_tests_docker.sh
   ```

2. **Run tests locally**
   ```bash
   cd backend
   chmod +x run_tests.sh
   ./run_tests.sh
   ```

3. **Run specific tests**
   ```bash
   docker-compose exec -e TESTING=true backend python -m pytest tests/api/v1/test_main.py -v
   ```

For more details about the testing framework, see the [Testing Documentation](./backend/tests/README.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.