#!/usr/bin/env bash

set -uxe
VERSION=$1
GIT_REVISION=$2
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker run --privileged --rm tonistiigi/binfmt --install all # This installs the emulator to build multi-arch images
set +e # Disable exit if the next command fails if the builder already exist.
docker buildx create --name octavia_builder > /dev/null 2>&1
set -e # The previous command can fail safely if
docker buildx use octavia_builder
docker buildx inspect --bootstrap
docker buildx build --push --tag airbyte/octavia-cli:${VERSION} --platform=linux/arm64,linux/amd64 --label "io.airbyte.git-revision=${GIT_REVISION}" ${SCRIPT_DIR}
