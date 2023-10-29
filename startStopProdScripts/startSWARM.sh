#!/bin/bash

cd ..

# This script does the following:
# 1. Starts the swarm mode on the host
# 2. Creates the overlay network for DB-API communication

# Start the swarm mode on the host
docker swarm init

# Create the overlay network for DB-API communication
docker network create --driver overlay rainsim-db-api

# To add more nodes to the swarm, run the following command on the new node:
# docker swarm join --token <token> <ip>:<port>