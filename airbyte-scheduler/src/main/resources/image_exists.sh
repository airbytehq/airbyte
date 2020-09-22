#!/usr/bin/env bash

set -e

function _error() {
  echo "$@" && exit 1
}

function _usage() {
  _error "Usage: ./image_exists.sh imageName tag"
}

function docker_exists_in_remote() {
  curl --silent -f -lSL https://index.docker.io/v1/repositories/$1/tags/$2 > /dev/null
}

function docker_exists_in_local() {
  docker inspect --type=image "$1:$2" 2> /dev/null | jq '. | length'
}

main() {
  [[ $# -eq 2 ]] || _usage

  imageName=$1 ;
  shift
  tag=$1 ;
  shift

  LOCAL=$(docker_exists_in_local ${imageName} ${tag})
  REMOTE=$(if ! docker_exists_in_remote ${imageName} ${tag}; then echo 0; else echo 1; fi)

  if [[ $LOCAL -eq 0 && $REMOTE -eq 0 ]]; then
    exit 1
  else
    exit 0
  fi
}

main "$@"
