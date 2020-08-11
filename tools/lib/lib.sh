#!/usr/bin/env sh

VERSION=$(cat .env | grep "^VERSION=" | cut -d = -f 2)

error() {
  echo "$@"
  exit 1
}

assert_root() {
  [ -f .root ] || error "Must run from root"
}
