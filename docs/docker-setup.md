# Docker Setup Guide for Voice TTS Live2D Project

This guide will walk you through setting up the Voice TTS Live2D project using Docker, which simplifies the deployment process by containerizing all the necessary components.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- Git installed on your system
- At least 4GB of RAM available for Docker
- Internet connection to download the Docker images

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/voice-tts-live2d-project.git
cd voice-tts-live2d-project
```

### 2. Configure Environment Variables

Copy the example environment file and customize it with your settings:

```bash
cp .env.example .env
```

Open the `.env` file in your preferred text editor and update the following key settings:

- API keys for OpenAI, Anthropic, ElevenLabs, etc. (if you plan to use these services)
- PostgreSQL credentials (if you want to change them from the defaults)
- Redis configuration (if needed)
- Any other settings specific to your deployment

The most critical settings to change for a production environment are:

```
# Security settings
API_KEY_ENCRYPTION_KEY=your_secure_encryption_key
JWT_SECRET=your_secure_jwt_secret
```

Next, create a `.env.local` file in the frontend directory:

```bash
mkdir -p frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

This file tells the frontend where to find the backend API.

### 3. Build and Start the Docker Containers

```bash
docker-compose build
docker-compose up -d
```

This will:
1. Build all the necessary Docker images
2. Start the PostgreSQL database
3. Start the Redis cache
4. Start the backend FastAPI server
5. Start the frontend Next.js server

### 4. Run Database Migrations

After the containers are running, apply the database migrations:

```bash
docker-compose exec backend alembic upgrade head
```

This command initializes the database schema required by the application. It creates all the necessary tables, indexes, and relationships in the PostgreSQL database. This step is required only once when setting up a new instance, or when upgrading to a version with new database migrations.

For production deployments, it's recommended to back up the database before running migrations.

### 5. Create an Admin User

After the containers are running, create an admin user using the provided script:

```bash
docker-compose exec backend python scripts/create_admin.py --username admin --password secure_password
```

This script will:
1. Create an admin user with the specified credentials
2. Generate a JWT token for API access
3. Generate an encryption key for API key storage

Take note of the JWT token and encryption key that are displayed. You should update your `.env` file with the generated encryption key:

```
API_KEY_ENCRYPTION_KEY=generated_key_from_script
```

Then restart the backend to apply the changes:

```bash
docker-compose restart backend
```

### 6. Verify the Installation

1. Backend API: Open http://localhost:8000 in your browser
   - You should see the API welcome page
   - API documentation is available at http://localhost:8000/api/docs

2. Frontend: Open http://localhost:3000 in your browser
   - You should see the application login page
   - Use the admin credentials created earlier to log in

### 7. Working with the Running Containers

#### Viewing Logs

```bash
# View logs from all services
docker-compose logs

# View logs from a specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs redis

# Follow the logs in real-time
docker-compose logs -f
```

#### Restarting Services

```bash
# Restart a specific service
docker-compose restart backend
docker-compose restart frontend

# Restart all services
docker-compose restart
```

#### Stopping Services

```bash
# Stop all services but keep the data volumes
docker-compose down

# Stop all services and remove all data volumes (use with caution)
docker-compose down -v
```

### 8. Troubleshooting Common Issues

#### CORS Issues

If you encounter CORS errors, check your `.env` file and ensure the `BACKEND_CORS_ORIGINS` setting is correctly formatted. The correct format is a comma-separated list:

```
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000
```

#### Database Connection Issues

If the backend cannot connect to the database, ensure:
1. The PostgreSQL container is running: `docker-compose ps`
2. The database connection settings in `.env` are correct
3. The database has been initialized: `docker-compose exec backend alembic upgrade head`

#### API Key Validation Errors

If you see errors related to API key validation, check:
1. The `API_KEY_ENCRYPTION_KEY` in your `.env` file is valid
2. The `prepare_fernet_key` function in `backend/app/core/security.py` is working correctly
3. You're using properly formatted keys in your requests

#### Port Conflicts

If you see errors about ports being already in use:
1. Check if another application is using the same ports
2. Modify the port mappings in `docker-compose.yml` to use different ports
3. Update the corresponding settings in your `.env` file

### 9. Production Deployment Considerations

For production deployments, consider the following:

1. Use secure, randomly generated values for all secrets and keys
2. Set `DEBUG=false` in your `.env` file
3. Use a proper domain with HTTPS
4. Update the CORS settings to include only your production domains
5. Set up proper backup strategies for the database
6. Configure rate limiting appropriate for your expected traffic
7. Set up monitoring and alerting
8. Consider using a managed database service instead of the containerized PostgreSQL

## Advanced Configuration

### Custom Live2D Models

Place your Live2D models in the `models/live2d` directory in the format:

```
models/
  live2d/
    model_name/
      model.model3.json
      textures/
      motions/
```

### Custom RVC Voice Models

Place your RVC voice models in the `models/rvc` directory in the format:

```
models/
  rvc/
    voice_name/
      config.json
      model.pth
      index.bin
```

### Custom LLM Models (Optional)

If using local LLMs, place them in `models/llm` and configure them in the backend settings.

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Live2D Cubism SDK Documentation](https://docs.live2d.com/)
- [RVC Documentation](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) 