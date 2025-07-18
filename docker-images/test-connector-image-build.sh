#!/bin/bash

# Test ability to build a connector image.
# Usage: ./test-connector-image-build.sh CONNECTOR_TYPE CONNECTOR_NAME

set -euo pipefail

CONNECTOR_TYPE=$1
CONNECTOR_NAME=$2
CONNECTOR_DIR="../airbyte-integrations/connectors/${CONNECTOR_NAME}"

BASE_IMAGE_NAME="docker.io/airbyte/${CONNECTOR_TYPE}-connector-base"
BASE_IMAGE_TAG='dev'

PRIMARY_ARCH='arm64'
IMAGE_TO_BUILD="airbyte/${CONNECTOR_TYPE}-connector"
TAG='dev'

./test-base-image-build.sh ${CONNECTOR_TYPE} ${BASE_IMAGE_TAG}

export DOCKER_BUILDKIT=1

ARCHES=(arm64 amd64)
for ARCH in "${ARCHES[@]}"; do
  echo "Building '${ARCH}' image: ${IMAGE_TO_BUILD}:${TAG}-${ARCH}"

  docker build \
    --platform linux/${ARCH} \
    --label io.airbyte.version=3.11.15\
    --label io.airbyte.name=airbyte/${CONNECTOR_NAME} \
    --file Dockerfile.${CONNECTOR_TYPE}-connector \
    --build-arg=BASE_IMAGE=${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}-${ARCH} \
    --build-arg=CONNECTOR_NAME=${CONNECTOR_NAME} \
    --build-arg=EXTRA_BUILD_SCRIPT= \
    -t ${IMAGE_TO_BUILD}:${TAG}-${ARCH} \
    ${CONNECTOR_DIR}
done

docker tag ${IMAGE_TO_BUILD}:${TAG}-${PRIMARY_ARCH} airbyte/${CONNECTOR_NAME}:dev
echo -e "Built images:\n- ${IMAGE_TO_BUILD}:${TAG}-${PRIMARY_ARCH}\n- ${IMAGE_TO_BUILD}:${TAG} ('${TAG}-${PRIMARY_ARCH}' alias)"
echo -e "Test by running: \n  docker run --rm -it ${IMAGE_TO_BUILD}:${TAG}-${PRIMARY_ARCH} spec"
