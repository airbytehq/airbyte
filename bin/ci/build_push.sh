#!/bin/bash

set -euo pipefail

DOCKER_BUILDKIT=1
DOCKER_REPOSITORY="${DOCKER_REGISTRY}"/"${IMAGE_NAME}"

docker pull "${DOCKER_REPOSITORY}":"${IDENTIFIER}" ||
docker build \
  -t "${DOCKER_REPOSITORY}":"${IDENTIFIER}" \
  -f "${DOCKER_FILE_PATH}" \
  .

docker tag "${DOCKER_REPOSITORY}":"${IDENTIFIER}" "${DOCKER_REPOSITORY}":"${APP_VERSION}"
docker tag "${DOCKER_REPOSITORY}":"${IDENTIFIER}" "${DOCKER_REPOSITORY}":"latest"

docker push "${DOCKER_REPOSITORY}":"${IDENTIFIER}"
docker push "${DOCKER_REPOSITORY}":"${APP_VERSION}"
docker push "${DOCKER_REPOSITORY}:latest"
