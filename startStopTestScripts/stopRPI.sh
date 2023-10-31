#!/bin/bash

cd ..

# This script does the following:
# 1. Stops the RPI compose

source .env

# Stop the RPI compose
cd ./rpi
docker compose down