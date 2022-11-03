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

  echo "Checking if ${imageName} exists..."
  # handle the case where the image exists ONLY on the local machine.
  LOCAL=$(docker_exists_in_local ${imageName})

  if [[ $LOCAL -eq 0 ]]; then
    echo "${imageName} not found locally. Attempting to pull the image..."
    # handle the case where the image exists in the remote and either has never been pulled or has already been pulled
    # and is already up to date.
    RESULT=$(docker pull $imageName 2> /dev/null | awk '/Status: Image is up to date/ || /Status: Downloaded newer image/')
    [ -z "$RESULT" ] && _error "Image does not exist."
    echo "Pulled ${imageName} from remote."
  else
    echo "${imageName} was found locally."
  fi

  exit 0
}

main "$@"
