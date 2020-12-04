#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

VERSION=$(cat .env | grep VERSION= | cut -d= -f 2)
[[ -z "$VERSION" ]] && echo "Couldn't find version in env file..." && exit 1

GIT_REVISION=$(git rev-parse HEAD)
[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

[[ ! -z "$(git status --porcelain)" ]] && echo "Cannot tag revision if all changes aren't checked in..." && exit 1

echo "Building and publishing version $VERSION for git revision $GIT_REVISION..."
./gradlew clean build
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml -f docker-compose.yaml build
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.normalization.build.yaml -f docker-compose.normalization.yaml build
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml -f docker-compose.yaml push
GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.normalization.build.yaml -f docker-compose.normalization.yaml push
echo "Completed building and publishing..."

echo "Tagging git revision..."
TAG_NAME="v$VERSION"
git tag -a "$TAG_NAME" -m "Version $VERSION"
git push origin "$TAG_NAME"
echo "Completed..."
