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

if [[ -z "${DOCKER_PASSWORD}" ]]; then
  echo 'DOCKER_PASSWORD for airbytebot not set.';
  exit 1;
fi

docker login -u airbytebot -p "${DOCKER_PASSWORD}"

source ./tools/bin/bump_version.sh

echo "Building and publishing PLATFORM version $NEW_VERSION for git revision $GIT_REVISION..."
VERSION=$NEW_VERSION SUB_BUILD=PLATFORM ./gradlew clean build
VERSION=$NEW_VERSION SUB_BUILD=PLATFORM ./gradlew publish
VERSION=$NEW_VERSION GIT_REVISION=$GIT_REVISION docker-compose -f docker-compose.build.yaml push
echo "Completed building and publishing PLATFORM..."
