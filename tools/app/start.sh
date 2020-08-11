#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

PORT=${PORT:-8080}

main() {
  assert_root
  docker-compose -f docker-compose.dev.yaml up --build
}

main "$@"
