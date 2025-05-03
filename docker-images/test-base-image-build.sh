#!/bin/bash

# Test ability to build the base image for a connector type (python or java).
# Usage: ./test-base-image-build.sh CONNECTOR_TYPE

set -euo pipefail

CONNECTOR_TYPE=$1
IMAGE_TO_BUILD="docker.io/airbyte/${CONNECTOR_TYPE}-connector-base"

ARCH='arm64'
TAG='dev'
CONTEXT_DIR="."  # This doesn't matter, since nothing is copied from the context dir.

export DOCKER_BUILDKIT=1

docker build \
    --platform linux/${ARCH} \
    --file Dockerfile.${CONNECTOR_TYPE}-connector-base \
    -t ${IMAGE_TO_BUILD}:${TAG} \
    ${CONTEXT_DIR}
