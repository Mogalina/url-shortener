#!/bin/bash

# Ensure we are in the project root directory
cd "$(dirname "$0")"

echo "==> Initializing URL Shortener Service..."

# Check for .env file; create it if missing
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo ".env file not found. Creating from .env.example..."
        cp .env.example .env
    else
        echo "Error: .env.example not found. Cannot configure environment."
        exit 1
    fi
else
    echo ".env file found."
fi

# Build and run with Docker Compose
echo "==> Building and starting containers..."
docker compose -f deploy/docker/docker-compose.yml --project-directory . up -d --build

# Application health check
if [ $? -eq 0 ]; then
    echo ""
    echo "Application is running!"
    docker compose -f deploy/docker/docker-compose.yml --project-directory . logs -f
else
    echo "Failed to start application."
    exit 1
fi
