#!/usr/bin/env bash

set -ux
VERSION=$1
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker buildx create --name octavia_builder > /dev/null 2>&1
set -e
docker buildx use octavia_builder
docker buildx inspect --bootstrap
docker buildx build --push --tag airbyte/octavia-cli:${VERSION} --platform=linux/arm64,linux/amd64 ${SCRIPT_DIR}
