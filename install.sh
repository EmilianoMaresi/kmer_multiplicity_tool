#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

IMAGE_NAME="kmer_multiplicity_tool"

echo "=================================================="
echo " Starting Docker Build for: ${IMAGE_NAME}"
echo "=================================================="

# 1. Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# 2. Check if the Docker daemon is actually running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running. Please start Docker."
    exit 1
fi

# 3. Optional: Remove old image to save space and ensure a fresh build
if [ "$(docker images -q ${IMAGE_NAME} 2> /dev/null)" ]; then
    echo "Found an existing version of ${IMAGE_NAME}. Removing it..."
    docker rmi -f ${IMAGE_NAME}
fi

# 4. Build the image
echo "🚀 Building the Docker image..."
docker build -t "${IMAGE_NAME}" .

echo "=================================================="
echo "Build complete! Image tagged as: ${IMAGE_NAME}"
echo "=================================================="
echo "You can now run your tool using:"
echo "docker run --rm -v \$(pwd)/data:/app/data -v \$(pwd)/results:/app/results ${IMAGE_NAME} -i /app/data/YOUR_DATASET -k 6"
echo "=================================================="
