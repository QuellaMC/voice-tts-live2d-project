#!/bin/bash

# Run tests in Docker using the test-specific docker-compose file
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build backend

# Return the exit code
exit $? 