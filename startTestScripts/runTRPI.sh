#!/bin/bash

cd ..

# This script does the following:
# 1. Set the environment variables
# 2. Run the RPI compose

# Set the environment variables
source .env

# Run the RPI compose
cd ./rpi
docker compose up 