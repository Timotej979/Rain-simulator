#!/bin/bash

cd ..

# This script does the following:
# 1. Leave the Docker Swarm and stop it
# 2. Remove the overlay network

# Leave the Docker Swarm and stop it
docker swarm leave --force

# Remove the overlay network
docker network rm rainsim-db-api