# Backend Tests

This directory contains tests for the backend API of the Voice TTS Live2D project.

## Test Structure

- `conftest.py`: Contains test fixtures and configuration
- `models.py`: Contains test-specific models for SQLite compatibility
- `mocks.py`: Contains mock services for testing
- `test_main_app.py`: Tests for the main application endpoints (root, health)
- `api/v1/`: Contains tests for API endpoints
  - `test_main.py`: Tests for main endpoints (health check, docs)
  - `test_auth.py`: Tests for authentication endpoints
  - `test_knowledge.py`: Tests for knowledge management endpoints
  - `test_root.py`: Tests for API root endpoints

## Current Test Status

### Working Tests
- ✅ Main application root endpoint
- ✅ Main application health check endpoint
- ✅ Health check endpoint
- ✅ API documentation endpoints
- ✅ Login endpoint
- ✅ Password reset request endpoint
- ✅ Knowledge management endpoints (list, create, get, update, delete, search)
- ✅ Root endpoints (root, health)

### Tests with Issues
- ❌ Refresh token endpoint (database-related issues)
- ❌ Logout endpoint (database-related issues)
- ❌ Tag management endpoints (require more complex mocking)
- ❌ User management endpoints (database-related issues)

## Running Tests

### Using Docker (Recommended)

The easiest way to run tests is using Docker with our test-specific configuration:

```bash
# From the project root
chmod +x run_tests_docker.sh
./run_tests_docker.sh
```

### Using Docker Compose Directly

```bash
# From the project root
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build backend
```

### Using Docker Compose Exec

To run all tests:
```bash
docker-compose exec -e TESTING=true backend python -m pytest
```

To run specific tests:
```bash
docker-compose exec -e TESTING=true backend python -m pytest tests/api/v1/test_main.py
docker-compose exec -e TESTING=true backend python -m pytest tests/api/v1/test_auth.py::test_login
docker-compose exec -e TESTING=true backend python -m pytest tests/api/v1/test_knowledge.py
```

To run tests with coverage:
```bash
docker-compose exec -e TESTING=true backend python -m pytest tests/api/v1/test_knowledge.py --cov=app.api.v1.endpoints.knowledge
```

### Using the Run Script

If you're developing directly on the backend:

```bash
# From the backend directory
chmod +x run_tests.sh
./run_tests.sh
```

## Test Database

The tests use an in-memory SQLite database instead of PostgreSQL to avoid the need for a database server during testing. This approach has some limitations:

- SQLite doesn't support all PostgreSQL features
- Some models (like Knowledge) have compatibility issues with SQLite's lack of array types

## Authentication in Tests

The tests use JWT tokens for authentication. The tokens are generated with a far future expiration date to avoid token expiration during testing.

## Mock Services

The following services are mocked for testing:
- `UserService`: Handles user authentication and management
- `TTSService`: Handles text-to-speech conversion
- `Live2DService`: Handles Live2D model management
- `CompanionService`: Handles companion management
- `EmbeddingsService`: Handles embeddings for knowledge search

## Dependencies

The tests require the following dependencies:
- pytest==8.3.4
- pytest-cov==6.0.0
- pytest-mock==3.14.0
- httpx==0.24.1
- opentelemetry-api==1.21.0
- opentelemetry-sdk==1.21.0
- opentelemetry-exporter-otlp==1.21.0
- opentelemetry-instrumentation-fastapi==0.42b0
- opentelemetry-instrumentation-sqlalchemy==0.42b0
- opentelemetry-semantic-conventions==0.42b0
- setuptools>=65.5.1

These dependencies are automatically installed when using the Docker setup or the `install_test_deps.sh` script.

## Recent Improvements

- Fixed SQLAlchemy deprecation warnings by updating imports
- Implemented comprehensive tests for knowledge management endpoints
- Added proper mocking for authentication dependencies
- Configured CI workflow to run tests with SQLite
- Replaced deprecated Jaeger exporter with OTLP exporter
- Added TESTING environment variable to disable tracing during tests
- Fixed pkg_resources deprecation warning by updating setuptools
- Created Docker Compose configuration for testing
- Added scripts for easy test execution

## Recommendations for Improvement

1. **Fix User Model Relationships**: Resolve the ambiguous foreign keys issue in the User model's relationship to groups.
2. **Ensure SQLite Compatibility**: Update models to be compatible with SQLite for testing (e.g., replace ARRAY types).
3. **Enhance Dependency Injection**: Improve the dependency injection system to make testing easier.
4. **Increase Test Coverage**: Add tests for remaining endpoints and edge cases.
5. **Set Up Continuous Integration**: Configure GitHub Actions to run tests automatically on pull requests.
6. **Set Up Jaeger Server**: Configure a Jaeger server for local development to enable tracing. 