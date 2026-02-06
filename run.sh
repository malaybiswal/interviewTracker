#!/bin/bash

# Interview Tracker Startup Script

echo "Starting Interview Tracker Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Build and run the application
echo "Building Docker image..."
docker build -t interview-tracker .

# Stop and remove existing container if it exists
echo "Checking for existing container..."
if docker ps -a --format 'table {{.Names}}' | grep -q "interview-tracker-app"; then
    echo "Stopping existing container..."
    docker stop interview-tracker-app 2>/dev/null || true
    echo "Removing existing container..."
    docker rm interview-tracker-app 2>/dev/null || true
fi

echo "Starting container..."
docker run -d \
  --name interview-tracker-app \
  -p 5080:5080 \
  -e DB_HOST=192.168.1.186 \
  -e DB_PORT=3306 \
  -e DB_USER=marisa \
  -e DB_PASSWORD=marisa@123 \
  -e DB_NAME=misc \
  -e JWT_SECRET_KEY=asghjas567as \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=false \
  interview-tracker

echo "Application started! Access it at http://localhost:5080"
echo "To view logs: docker logs interview-tracker-app"
echo "To stop: docker stop interview-tracker-app"