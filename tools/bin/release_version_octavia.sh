#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

if test -z "${DOCKER_HUB_USERNAME}"; then
  echo 'DOCKER_HUB_USERNNAME not set.';
  exit 1;
fi

if test -z "${DOCKER_HUB_PASSWORD}"; then
  echo 'DOCKER_HUB_PASSWORD for docker user not set.';
  exit 1;
fi

docker login --username "${DOCKER_HUB_USERNAME}" --password "${DOCKER_HUB_PASSWORD}"

source ./tools/bin/bump_version.sh

echo "Building and publishing OCTAVIA version ${NEW_VERSION} for git revision ${GIT_REVISION}..."
VERSION=$NEW_VERSION SUB_BUILD=OCTAVIA_CLI ./gradlew clean build
./octavia-cli/publish.sh ${NEW_VERSION} ${GIT_REVISION}
echo "Completed building and publishing OCTAVIA..."
