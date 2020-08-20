#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root
  docker exec --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.gradle:/home/gradle/.gradle server-base:dev "./gradlew test --no-daemon --console rich -g /home/gradle/.gradle"
}

main "$@"

