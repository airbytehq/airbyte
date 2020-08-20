#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.gradle:/home/gradle/.gradle -t dataline/server-base:latest /bin/sh -c ./gradlew test --no-daemon --console rich -g /home/gradle/.gradle
  docker run --rm -t dataline/webapp-base:latest /bin/sh -c 'npm run test'
}

main "$@"
