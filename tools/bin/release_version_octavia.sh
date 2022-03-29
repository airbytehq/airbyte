#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

if [[ -z "${DOCKER_PASSWORD}" ]]; then
  echo 'DOCKER_PASSWORD for airbytebot not set.';
  exit 1;
fi

docker login -u airbytebot -p "${DOCKER_PASSWORD}"

NEW_VERSION=$(grep -w VERSION .env | cut -d"=" -f2)
GIT_REVISION=$(git rev-parse HEAD)

[[ -z "$GIT_REVISION" ]] && echo "Couldn't get the git revision..." && exit 1

VERSION=$NEW_VERSION SUB_BUILD=OCTAVIA_CLI ./gradlew clean build
./octavia-cli/publish.sh ${NEW_VERSION} ${GIT_REVISION}
