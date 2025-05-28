#!/bin/bash

# Test ability to build the base image for a connector type (python or java).
# Usage: ./test-base-image-build.sh CONNECTOR_TYPE

set -euo pipefail

CONNECTOR_TYPE=$1
IMAGE_TO_BUILD="docker.io/airbyte/${CONNECTOR_TYPE}-connector-base"

TAG='dev'
PRIMARY_ARCH='arm64'  # This will get aliased to 'dev' in the final image.
CONTEXT_DIR="."  # This doesn't matter, since nothing is copied from the context dir.

export DOCKER_BUILDKIT=1

# build for both architectures without duplicating the docker build command
ARCHES=(arm64 amd64)
for ARCH in "${ARCHES[@]}"; do
  echo "Building '${ARCH}' image: ${IMAGE_TO_BUILD}:${TAG}-${ARCH}"
  docker build \
    --platform linux/${ARCH} \
    --file Dockerfile.${CONNECTOR_TYPE}-connector-base \
    -t ${IMAGE_TO_BUILD}:${TAG}-${ARCH} \
    ${CONTEXT_DIR}
done

echo -e "Built base images:\n- ${IMAGE_TO_BUILD}:${TAG}-amd64\n- ${IMAGE_TO_BUILD}:${TAG}-arm64\n- ${IMAGE_TO_BUILD}:${TAG} ('dev-${PRIMARY_ARCH}' alias)"
