#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

IMG_NAME=dataline/build-project:dev

main() {
  assert_root

  docker build -f Dockerfile.build . -t $IMG_NAME --target build-project

  docker run -t --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd):/code \
    -v ~/.gradle:/home/gradle/.gradle \
    -v $(which docker):/bin/docker \
    $IMG_NAME ./gradlew --no-daemon -g /home/gradle/.gradle "$@"
}

main "$@"
