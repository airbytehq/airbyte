#!/usr/bin/env bash

set -ux
VERSION=$1

docker login -u airbytebot -p "${DOCKER_PASSWORD}"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
docker run --privileged --rm tonistiigi/binfmt --install all
docker build --push --tag airbyte/octavia-cli:${VERSION} ${SCRIPT_DIR}
docker buildx create --name octavia_builder > /dev/null 2>&1
set -e
docker buildx use octavia_builder
docker buildx inspect --bootstrap
docker buildx build --push --tag airbyte/octavia-cli:${VERSION} --platform=linux/arm64,linux/amd64 ${SCRIPT_DIR}
