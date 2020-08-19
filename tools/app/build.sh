#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

BASE_IMAGE_DOCKERFILE=server_base.Dockerfile
BASE_IMAGE_NAME=dataline/server/base

DIST_IMAGE_DOCKERFILE=server_dist.Dockerfile
DIST_IMAGE_NAME=dataline/server

main() {
  assert_root
  docker build -f "$BASE_IMAGE_DOCKERFILE" . -t "$BASE_IMAGE_NAME"
  # The base image may launch docker containers, so mount the docker socket as a volume to allow that
  docker run -t --rm -v /var/run/docker.sock:/var/run/docker.sock "$BASE_IMAGE_NAME"
  docker build -f "$DIST_IMAGE_DOCKERFILE" . -t "$DIST_IMAGE_NAME"
  docker-compose -f docker-compose.dev.yaml build --parallel
}

main "$@"
