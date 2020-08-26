#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root

  echo "Building images..."
  docker-compose -f docker-compose.yaml -f docker-compose.build.yaml build
}

main "$@"
