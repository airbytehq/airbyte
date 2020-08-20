#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

BASE_IMAGE_DOCKERFILE=server_base.Dockerfile
BASE_IMAGE_NAME=dataline/server/base

main() {
  assert_root
  echo "Building base image..."
  docker build -f "$BASE_IMAGE_DOCKERFILE" . -t "$BASE_IMAGE_NAME"

  echo "Running base build..."
  # The base image may launch docker containers, so mount the docker socket as a volume to allow that
  docker run -t --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.gradle:/home/gradle/.gradle "$BASE_IMAGE_NAME"

  echo "Running docker-compose..."
  docker-compose -f docker-compose.dev.yaml build --parallel
}

main "$@"
