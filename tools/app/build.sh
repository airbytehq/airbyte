#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root

  echo "Building server-base..."
  docker build -f server_base.Dockerfile . -t dataline/server-base:dev

  echo "Building webapp-base..."
  docker build -f webapp_base.Dockerfile . -t dataline/webapp-base:dev

  echo "Running docker-compose..."
  docker-compose -f docker-compose.dev.yaml build --parallel
}

main "$@"
