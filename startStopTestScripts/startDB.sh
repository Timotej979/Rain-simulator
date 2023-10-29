#!/bin/bash

cd ..

# This script does the following:
# 1. Set the environment variables
# 2. Create the network for DB-API communication
# 2. Run the DB compose

# Set the environment variables
source .env

# Create the network for DB-API communication
docker network create db-api

# Run the DB compose
cd ./database
docker compose up -d