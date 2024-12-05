#!/usr/bin/env bash

set -e

ROOT_DIR="$1"
PROJECT_DIR="$2"
DOCKERFILE="$3"
TAGGED_IMAGE="$4"
ID_FILE="$5"
DOCKER_BUILD_ARCH="${DOCKER_BUILD_ARCH:-amd64}"
# https://docs.docker.com/develop/develop-images/build_enhancements/
export DOCKER_BUILDKIT=1

cd "$ROOT_DIR"
. tools/lib/lib.sh
assert_root

cd "$PROJECT_DIR"

args=(
    -f "$DOCKERFILE"
    -t "$TAGGED_IMAGE"
    --iidfile "$ID_FILE"
)

JDK_VERSION="${JDK_VERSION:-17.0.8}"
if [[ -z "${DOCKER_BUILD_PLATFORM}" ]]; then
  docker build --build-arg JDK_VERSION="$JDK_VERSION" --build-arg DOCKER_BUILD_ARCH="$DOCKER_BUILD_ARCH" . "${args[@]}"
else
  docker build --build-arg JDK_VERSION="$JDK_VERSION" --build-arg DOCKER_BUILD_ARCH="$DOCKER_BUILD_ARCH" --platform="$DOCKER_BUILD_PLATFORM" . "${args[@]}"
fi
