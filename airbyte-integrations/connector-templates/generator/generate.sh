#!/usr/bin/env bash

set -eo pipefail

IMAGE_NAME=connector-generator
CONTAINER_NAME=airbyte-connector-generator-${RANDOM}

_ensure_environment() {
  # Make sure docker is running before trying
  docker ps || { echo "docker is not running, please start up the docker daemon"; exit 1; }

  # Ensure script always runs from this directory because that's how docker build contexts work
  cd "$(dirname "${0}")" || exit 1
}

main() {
  _ensure_environment

  docker build . -t "${IMAGE_NAME}"

  echo "Running generator (${CONTAINER_NAME})"
  docker run --rm -it \
    -v "$(pwd)/../../../.":/airbyte \
    --name "$CONTAINER_NAME" "${IMAGE_NAME}"
}

main "$@"
