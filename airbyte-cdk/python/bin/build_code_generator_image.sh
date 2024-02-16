#!/usr/bin/env bash

set -e

DOCKER_BUILD_ARCH="${DOCKER_BUILD_ARCH:-amd64}"
# https://docs.docker.com/develop/develop-images/build_enhancements/
export DOCKER_BUILDKIT=1

CODE_GENERATOR_DOCKERFILE="$(dirname $0)/../code-generator/Dockerfile"
test -f $CODE_GENERATOR_DOCKERFILE
docker build --build-arg DOCKER_BUILD_ARCH="$DOCKER_BUILD_ARCH" -t "airbyte/code-generator:dev" - < $CODE_GENERATOR_DOCKERFILE
