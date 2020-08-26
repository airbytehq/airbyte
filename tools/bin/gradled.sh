#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

IMG_NAME=dataline/build-project:dev

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

  docker build -q -f Dockerfile.build . -t $IMG_NAME --target build-project

  ./gradlew clean
  docker run $OPTS --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v ~/.gradle:/root/.gradle \
    -v $(pwd):/code \
    -e GRADLE_OPTS="-Dorg.gradle.daemon=false" \
    $IMG_NAME $CMD
}

main "$@"
