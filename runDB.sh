#!/bin/bash

# This script does the following:
# 1. Set the environment variables 
# 2. Create an external network for the database container
# 3. Run the database container as a daemon

# Set the environment variables
source .env

# Create an external network for the database container
docker network create rainsim-db-api

# Run the database container
cd ./database
docker compose up -d