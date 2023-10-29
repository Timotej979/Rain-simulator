#!/bin/bash

cd ..

# This script does the following:
# 1. Stops the DB compose

# Stop the DB compose
cd ./database
docker compose down