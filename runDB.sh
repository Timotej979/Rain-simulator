#!/bin/bash

# This script does the following:
# 1. Set the environment variables 
# 1. Run the database container as a daemon

# Set the environment variables
source .env

# Run the database container
cd ./database
docker-compose up -d