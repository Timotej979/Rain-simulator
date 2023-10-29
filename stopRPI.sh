#!/bin/bash

# This script does the following:
# 1. Stops the RPI containers:
#   a. rain-simulator-api
#   b. rain-simulator-nginx

# Stop the RPI containers
docker stop rain-simulator-api
docker stop rain-simulator-nginx