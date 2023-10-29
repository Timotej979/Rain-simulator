#!/bin/bash

cd ..

# This script does the following:
# 1. Set the environment variables 
# 2. Run the database container in swarm stack

# Set the environment variables
source .env

# Run the database container
cd ./database
docker stack deploy -c stack-db.yml db-stack