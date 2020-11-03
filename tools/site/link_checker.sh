#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

function publish() {
  local image_name; image_name=$(_get_docker_image_name "$SCRIPT_DIRECTORY"/link_checker.Dockerfile)

  (cd "$SCRIPT_DIRECTORY" && docker build -q -f link_checker.Dockerfile -t $image_name .)
  docker push $image_name
}

function run() {
  local image_name; image_name=$(_get_docker_image_name "$SCRIPT_DIRECTORY"/link_checker.Dockerfile)

  docker run "$image_name" "$@"
}

function main() {
  assert_root
  
  if [ "$1" = publish ]; then
    publish
  elif [ "$1" = run ]; then
    shift
    run "$@"
  elif [ "$1" = check_docs ]; then
    local res; res=$(mktemp)

    run https://docs.airbyte.io -r --filter-level 1 | grep -E '(^Getting|HTTP_404)' > $res
    grep -q BROKEN $res && error "Found broken links: \n$(cat $res)"
  else
    error "Unknown command: $1"
  fi
}

main "$@"
