#!/bin/bash

# Test ability to build a connector image.
# Usage: ./test-connector-image-build.sh CONNECTOR_TYPE CONNECTOR_NAME

set -euo pipefail

CONNECTOR_TYPE=$1
CONNECTOR_NAME=$2
CONNECTOR_DIR="../airbyte-integrations/connectors/${CONNECTOR_NAME}"

BASE_IMAGE_NAME="docker.io/airbyte/${CONNECTOR_TYPE}-connector-base"
BASE_IMAGE_TAG='dev'

ARCH='arm64'

./test-base-image-build.sh ${CONNECTOR_TYPE} ${BASE_IMAGE_TAG}

export DOCKER_BUILDKIT=1

docker build \
    --platform linux/${ARCH} \
    --label io.airbyte.version=3.11.15\
    --label io.airbyte.name=airbyte/${CONNECTOR_NAME} \
    --file Dockerfile.${CONNECTOR_TYPE}-connector \
    --build-arg=BASE_IMAGE=${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG} \
    --build-arg=CONNECTOR_NAME=${CONNECTOR_NAME} \
    --build-arg=EXTRA_BUILD_SCRIPT= \
    -t airbyte/${CONNECTOR_NAME}:dev-${ARCH} \
    ${CONNECTOR_DIR}

docker tag airbyte/${CONNECTOR_NAME}:dev-${ARCH} airbyte/${CONNECTOR_NAME}:dev
echo -e "Built images:\n- airbyte/${CONNECTOR_NAME}:dev-${ARCH}\n- airbyte/${CONNECTOR_NAME}:dev ('dev-${ARCH}' alias)"

echo -e "Test by running: \n  docker run --rm -it airbyte/${CONNECTOR_NAME}:dev-${ARCH} spec"
