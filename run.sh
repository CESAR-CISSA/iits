#!/bin/bash

# Shell script for quick environment initialization

# Check if docker and docker-compose are installed
# If not, prompt the user to install them
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker compose not found. Please install Docker compose first."
    exit 1
fi