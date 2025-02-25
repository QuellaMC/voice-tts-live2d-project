# Contributing to AI Anime Companion

Thank you for your interest in contributing to the AI Anime Companion project! This document outlines the process for contributing to the project and how you can get involved.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

- **Use the GitHub issue tracker** to report bugs.
- **Use the bug report template** provided.
- **Include detailed steps to reproduce** the issue.
- **Describe the behavior you expected** to see.
- **Include screenshots** if possible.
- **Include environment details** such as OS, browser, etc.

### Suggesting Features

- **Use the GitHub issue tracker** to suggest features.
- **Use the feature request template** provided.
- **Provide a clear description** of the feature.
- **Explain why this feature would be useful** to most users.
- **Consider including mockups or diagrams** if applicable.

### Pull Requests

1. **Fork the repository**.
2. **Create a branch** with a descriptive name.
3. **Make your changes**, following the coding style guide.
4. **Write or update tests** if applicable.
5. **Update documentation** to reflect your changes.
6. **Submit a pull request** using the template provided.

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (recommended)

### Setting Up Local Development

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/voice-tts-live2d-project.git
   cd voice-tts-live2d-project
   ```

2. **Create a .env file** using the .env.example template:
   ```bash
   cp .env.example .env
   ```

3. **Start the development environment** using Docker:
   ```bash
   docker-compose up
   ```

   Or manually:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm install
   npm run dev
   ```

## Coding Guidelines

### Python (Backend)

- Follow PEP 8 style guide.
- Use type hints for function parameters and return values.
- Write docstrings for functions and classes.
- Use meaningful variable and function names.
- Include unit tests for new functionality.

### TypeScript/JavaScript (Frontend)

- Follow the ESLint configuration.
- Use TypeScript for type safety.
- Follow React best practices.
- Use functional components with hooks.
- Keep components small and focused.

## Testing

- **Write unit tests** for backend functionality.
- **Write component tests** for frontend components.
- **Run existing tests** before submitting a pull request.
- **Ensure all tests pass** before submitting changes.

## Documentation

- **Update README.md** if necessary.
- **Update documentation** in the docs/ directory.
- **Include JSDoc or docstrings** for code.
- **Provide usage examples** for API endpoints or UI components.

## Security

- **Never commit API keys** or secrets.
- **Use environment variables** for sensitive configuration.
- **Sanitize user inputs** to prevent injection attacks.
- **Follow security best practices** for authentication and data handling.

## Reviewing Pull Requests

When reviewing pull requests:
- **Be respectful and constructive**.
- **Consider the project goals**.
- **Verify the changes work as expected**.
- **Check for security implications**.
- **Ensure tests and documentation are updated**.

## License

By contributing to AI Anime Companion, you agree that your contributions will be licensed under the project's MIT License. 