#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root
  echo "Running docker-compose..."
  docker-compose -f docker-compose.dev.yaml build --parallel
}

main "$@"
