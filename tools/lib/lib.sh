#!/usr/bin/env sh

VERSION=$(cat .version)

error() {
  echo "$@"
  exit 1
}

assert_root() {
  [ -f .root ] || error "Must run from root"
}
