# AI Anime Companion (Voice-TTS-Live2D)

An interactive AI-powered anime companion with custom voice synthesis and Live2D animations.

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

2. **Set API keys in docker-compose.yml**
   Edit the docker-compose.yml file and update environment variables with your API keys and custom endpoints.

3. **Start the development environment**
   ```bash
   docker-compose up
   ```

4. **Create an admin account**
   ```bash
   cd scripts
   python create_admin.py --username admin
   ```

5. **Access the application**
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
- MongoDB for data storage
- Secure API key management and encryption

## Project Structure

```
ai-anime-companion/
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

For detailed setup and configuration instructions, see the [Setup Guide](./docs/setup.md).

For architecture and design details, see the [Architecture Documentation](./docs/architecture.md).

For the development roadmap, see the [Roadmap](./docs/roadmap.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.