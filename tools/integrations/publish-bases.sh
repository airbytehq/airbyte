#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"
cd "../.."

GIT_REVISION=$(git rev-parse HEAD)
VERSION=$(date +%Y%m%d)

BUILD_ARCH="linux/amd64,linux/arm64"

echo "--- PUBLISHING BASES ---"
echo "GIT_REVISION: $GIT_REVISION"
echo "VERSION: $VERSION"

# docker buildx create --name connector-buildx --driver docker-container --use

GIT_REVISION=$GIT_REVISION VERSION=$VERSION docker buildx bake \
  --set "*.platform=$BUILD_ARCH"                               \
  -f docker-compose.connector-bases.yaml                       \
  --push

# GIT_REVISION=$GIT_REVISION VERSION="latest" docker buildx bake \
#   --set "*.platform=$BUILD_ARCH"                               \
#   -f docker-compose.connector-bases.yaml                       \
#   --push

# docker buildx rm connector-buildx
