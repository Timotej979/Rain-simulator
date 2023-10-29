#!/bin/bash

# This script does the following:
# 1. Set the environment variables
# 2. Run the RPI container as a daemon

# Set the environment variables
source .env

# Run the RPI container
cd ./rpi
docker compose build
docker compose up