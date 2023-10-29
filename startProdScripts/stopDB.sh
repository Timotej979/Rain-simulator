#!/bin/bash

cd ..

# This script does the following:
# 1. Stops the DB in swarm stack

# Stop the DB in swarm stack
docker stack rm db-stack