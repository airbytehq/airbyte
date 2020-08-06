#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

main() {
  assert_root

  docker push dataline/conduit:$VERSION
}

main "$@"
