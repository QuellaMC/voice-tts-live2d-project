#!/bin/bash

# Install test dependencies
pip install pytest==8.3.4 pytest-cov==6.0.0 pytest-mock==3.14.0 httpx==0.24.1

# Install OpenTelemetry dependencies with correct versions
pip install opentelemetry-api==1.21.0 \
            opentelemetry-sdk==1.21.0 \
            opentelemetry-exporter-otlp==1.21.0 \
            opentelemetry-instrumentation-fastapi==0.42b0 \
            opentelemetry-instrumentation-sqlalchemy==0.42b0 \
            opentelemetry-semantic-conventions==0.42b0

# Install setuptools to fix pkg_resources deprecation warning
pip install setuptools>=65.5.1

# Make the script executable
chmod +x ./run_tests.sh

echo "Test dependencies installed successfully"

# Return the exit code
exit $? 