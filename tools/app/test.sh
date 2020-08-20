#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v ~/.gradle:/home/gradle/.gradle -it -d server-base:dev ./gradlew test --no-daemon --console rich -g /home/gradle/.gradle
  docker run --rm -it webapp:dev npm test
  # todo: use docker-compose run instead so it loads mounts correctly
}

main "$@"

