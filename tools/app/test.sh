#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root
  docker run -t --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.gradle:/home/gradle/.gradle dataline/java-base:dev ./gradlew test --no-daemon -g /home/gradle/.gradle
  docker run --rm -t dataline/webapp-base:dev /bin/sh -c 'CI=true npm run test'
}

main "$@"
