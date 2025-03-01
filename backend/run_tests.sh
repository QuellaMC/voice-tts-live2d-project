#!/bin/bash

# Set environment variables for testing
export TESTING=true
export TEST_DATABASE_URL="sqlite:///:memory:"
export JWT_SECRET="test-jwt-secret-for-testing"
export API_KEY_ENCRYPTION_KEY="TEST_KEY_NOT_REAL_FOR_TESTING_ONLY_1234567890"
export OPENAI_API_KEY="sk-test-key-not-real"

# Install required dependencies if not already installed
pip install -q setuptools>=65.5.1 pytest==8.3.4 pytest-cov==6.0.0 pytest-mock==3.14.0

# Run pytest with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Return the exit code from pytest
exit $? 