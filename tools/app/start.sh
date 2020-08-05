#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

PORT=${PORT:-8080}

main() {
  assert_root

  docker run --rm -it \
    -p $PORT:8080 \
    dataline/conduit:$VERSION
}

main "$@"
