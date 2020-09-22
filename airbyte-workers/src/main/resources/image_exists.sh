#!/usr/bin/env bash

set -e

function _error() {
  echo "$@" && exit 1
}

function _usage() {
  _error "Usage: ./image_exists.sh imageName"
}

function docker_exists_in_local() {
  docker inspect --type=image "$1" 2> /dev/null | jq '. | length'
}

main() {
  [[ $# -eq 1 ]] || _usage
  imageName=$1

  # handle the case where the image exists ONLY on the local machine.
  LOCAL=$(docker_exists_in_local ${imageName})

  if [[ $LOCAL -eq 0 ]]; then
    # handle the case where the image exists in the remote and either has never been pulled or has already been pulled
    # and is already up to date.
    RESULT=$(docker pull $imageName 2> /dev/null | awk '/Image is up to date/ || /Status: Downloaded newer image/')
    [ -z "$RESULT" ] && _error "Image does not exist."
  fi

  exit 0
}

main "$@"
