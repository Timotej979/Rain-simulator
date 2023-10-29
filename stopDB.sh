#!/bin/bash

# This script does the following:
# 1. Stops the database container
# 2. Removes the external network for the database container

# Stop the database container
docker stop rain-simulator-db

# Remove the external network for the database container
docker network rm rainsim-db-api