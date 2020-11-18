#!/usr/bin/env bash

set -e

ROOT_DIR="$1"
PROJECT_DIR="$2"
DOCKERFILE="$3"
TAG="$4"
ID_FILE="$5"

cd "$ROOT_DIR"
. tools/lib/lib.sh
assert_root

cd "$PROJECT_DIR"

if [[ -z "$CI" ]]; then
  # run standard build locally (not on CI)
  DOCKER_BUILDKIT=1 docker build \
    -f "$DOCKERFILE" . \
    -t "$TAG" \
    --iidfile "$ID_FILE"
else
  docker pull localhost:5000/"$TAG" || true
  docker build \
    -f "$DOCKERFILE" . \
    -t "$TAG" \
    --iidfile "$ID_FILE" \
    --cache-from localhost:5000/"$TAG"
  docker push localhost:5000/"$TAG"
fi



