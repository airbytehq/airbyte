#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

if [[ -z "${CLOUDREPO_USER}" ]]; then
  echo 'CLOUDREPO_USER env var not set. Please retrieve the user email from the CloudRepo lastpass secret and run export CLOUDREPO_USER=<user_from_secret>.';
  exit 1;
fi

if [[ -z "${CLOUDREPO_PASSWORD}" ]]; then
  echo 'CLOUDREPO_PASSWORD env var not set. Please retrieve the user email from the CloudRepo lastpass secret and run export CLOUDREPO_PASSWORD=<password_from_secret>.';
  exit 1;
fi

if [[ -z "${DOCKER_HUB_USERNAME}" ]]; then
  echo 'DOCKER_HUB_USERNAME not set.';
  exit 1;
fi

if [[ -z "${DOCKER_HUB_PASSWORD}" ]]; then
  echo 'DOCKER_HUB_PASSWORD for docker user not set.';
  exit 1;
fi

docker login -u "${DOCKER_HUB_USERNAME}" -p "${DOCKER_HUB_PASSWORD}"

source ./tools/bin/bump_version.sh

echo "Building and publishing PLATFORM version $NEW_VERSION for git revision $GIT_REVISION..."
VERSION=$NEW_VERSION SUB_BUILD=PLATFORM ./gradlew clean build
VERSION=$NEW_VERSION SUB_BUILD=PLATFORM ./gradlew publish

# Container should be running before build starts
# It generates binaries to build images for different CPU architecture
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
VERSION=$NEW_VERSION ./tools/bin/publish_docker.sh
echo "Completed building and publishing PLATFORM..."
