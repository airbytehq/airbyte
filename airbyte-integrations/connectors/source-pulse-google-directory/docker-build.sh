#!/usr/bin/env bash

# Exit on error
set -e

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Image name and version
IMAGE_NAME="airbyte/source-pulse-google-directory"
IMAGE_VERSION=$(grep "^version" "$SCRIPT_DIR/pyproject.toml" | cut -d'"' -f2)

# Make sure poetry.lock is up to date
poetry lock

# Build the image
docker build . -t "$IMAGE_NAME:dev" -t "$IMAGE_NAME:$IMAGE_VERSION" --platform linux/amd64

# Test the image
echo "Testing the image..."
docker run --rm -i "$IMAGE_NAME:dev" spec