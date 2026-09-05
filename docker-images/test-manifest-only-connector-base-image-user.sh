#!/bin/bash

# Test that manifest-only connector images require the airbyte user in their base image.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECTOR_DIR="${SCRIPT_DIR}/../airbyte-integrations/connectors/source-pokeapi"
IMAGE_NAME="airbyte/source-pokeapi:base-image-user-test"
OLD_BASE_IMAGE="docker.io/airbyte/source-declarative-manifest:5.15.0"
CURRENT_BASE_IMAGE="docker.io/airbyte/source-declarative-manifest:latest"

case "$(docker info --format '{{.Architecture}}')" in
  amd64|x86_64)
    PLATFORM="linux/amd64"
    ;;
  arm64|aarch64)
    PLATFORM="linux/arm64"
    ;;
  *)
    echo "Unsupported Docker architecture" >&2
    exit 1
    ;;
esac

export DOCKER_BUILDKIT=1

old_build_log="$(mktemp)"
trap 'rm -f "${old_build_log}"' EXIT

echo "Building with stale base image: ${OLD_BASE_IMAGE}"
if docker build \
  --progress=plain \
  --platform "${PLATFORM}" \
  --file "${SCRIPT_DIR}/Dockerfile.manifest-only-connector" \
  --build-arg="BASE_IMAGE=${OLD_BASE_IMAGE}" \
  --build-arg=CONNECTOR_NAME=source-pokeapi \
  --tag "${IMAGE_NAME}-old" \
  "${CONNECTOR_DIR}" 2>&1 | tee "${old_build_log}"; then
  echo "Expected the build to fail when the base image lacks the airbyte user" >&2
  exit 1
fi

grep -F "ERROR: base image ${OLD_BASE_IMAGE} does not contain the airbyte user. Bump connectorBuildOptions.baseImage in the connector's metadata.yaml." "${old_build_log}"

echo "Building with current base image: ${CURRENT_BASE_IMAGE}"
docker build \
  --progress=plain \
  --platform "${PLATFORM}" \
  --file "${SCRIPT_DIR}/Dockerfile.manifest-only-connector" \
  --build-arg="BASE_IMAGE=${CURRENT_BASE_IMAGE}" \
  --build-arg=CONNECTOR_NAME=source-pokeapi \
  --tag "${IMAGE_NAME}-current" \
  "${CONNECTOR_DIR}"
