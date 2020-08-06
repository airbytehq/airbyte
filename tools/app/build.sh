#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root

  docker build . -t dataline/conduit:$VERSION
}

main "$@"
