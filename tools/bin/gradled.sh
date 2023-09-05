#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

IMG_NAME=airbyte/build-project:dev
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

  docker run $OPTS --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/code \
    -p 5005:5005 \
    -e GRADLE_OPTS="-Dorg.gradle.daemon=false" \
    $IMG_NAME $CMD
}

main "$@"
