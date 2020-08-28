#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

IMG_NAME=dataline/build-project:dev
TMP_VOLUME_NAME=gradlew-tmp

main() {
  assert_root

  if [[ $# -gt 0 ]]; then
    OPTS=
    CMD="./gradlew $@"
  else
    OPTS=-it
    CMD=/bin/bash
  fi
  local args=${@:-/bin/bash}

  docker build -f Dockerfile.build . -t $IMG_NAME --target build-project

  docker volume rm --force $TMP_VOLUME_NAME >/dev/null || true
  docker volume create $TMP_VOLUME_NAME >/dev/null || true
  docker run $OPTS --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $TMP_VOLUME_NAME:/tmp \
    -v $(pwd):/code \
    -e GRADLE_OPTS="-Dorg.gradle.daemon=false" \
    $IMG_NAME $CMD
}

main "$@"
