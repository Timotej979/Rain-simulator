#!/bin/bash

cd ..

# This script does the following:
# 1. Set the environment variables
# 2. Run the RPI container in swarm stack

# Set the environment variables
source .env

# Run the RPI container
cd ./rpi

# Build the images
docker compose  build
docker compose up -d  
docker compose down

# Tag the images
docker tag rain-simulator-api:latest timotej979/rain-simulator-api:latest
docker tag rain-simulator-nginx:latest timotej979/rain-simulator-nginx:latest

# Push the images to Docker Hub
docker push timotej979/rain-simulator-api:latest
docker push timotej979/rain-simulator-nginx:latest

# Deploy the stack
docker stack deploy -c stack-rpi.yml rpi-stack