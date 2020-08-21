#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root

  echo "Building java-base..."
  docker build -f java_base.Dockerfile . -t dataline/java-base:dev

  echo "Building webapp-base..."
  docker build -f webapp_base.Dockerfile . -t dataline/webapp-base:dev

  echo "Running docker-compose..."
  docker-compose -f docker-compose.dev.yaml build --parallel
}

main "$@"
