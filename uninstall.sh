#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

IMAGE_NAME="kmer_multiplicity_tool"

echo "=================================================="
echo " Starting Docker Cleanup for: ${IMAGE_NAME}"
echo "=================================================="

# 1. Check if the Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running. Please start Docker."
    exit 1
fi

# 2. Stop and remove any containers currently running this image
if [ "$(docker ps -a -q -f ancestor=${IMAGE_NAME})" ]; then
    echo "Found containers running ${IMAGE_NAME}. Stopping and removing them..."
    docker rm -f $(docker ps -a -q -f ancestor=${IMAGE_NAME})
fi

# 3. Uninstall the main Docker image
if [ "$(docker images -q ${IMAGE_NAME} 2> /dev/null)" ]; then
    echo "🗑️ Removing Docker image: ${IMAGE_NAME}..."
    docker rmi -f ${IMAGE_NAME}
    echo "Image successfully uninstalled."
else
    echo "Image '${IMAGE_NAME}' was not found on this system. Skipping."
fi

# 4. Clean up unused space (dangling images, build cache, stopped container data)
echo "Purging unused Docker build cache and dangling layers..."
# --force skips the interactive confirmation prompt [y/N]
docker system prune -f --volumes

echo "=================================================="
echo "Cleanup complete! All space reclaimed."
echo "=================================================="
