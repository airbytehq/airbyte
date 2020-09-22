#!/usr/bin/env bash

set -e

function _error() {
  echo "$@" && exit 1
}

function _usage() {
  _error "Usage: ./image_exists.sh imageName"
}

main() {
  [[ $# -eq 1 ]] || _usage
  imageName=$1

  RESULT=$(docker pull $imageName 2> /dev/null | awk '/Image is up to date/ || /Status: Downloaded newer image/')
  [ -z "$RESULT" ] && _error "Image does not exist."
  exit 0
}

main "$@"
