#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

IMAGE_NAME=$(_get_docker_image_name "$SCRIPT_DIRECTORY"/link_checker.Dockerfile)

function build() {
  (cd "$SCRIPT_DIRECTORY" && docker build -q -f link_checker.Dockerfile -t "$IMAGE_NAME" .)
}

function publish() {
  build
  docker push "$IMAGE_NAME"
}

function run() {
  docker run "$IMAGE_NAME" "$@"
}

function check_docs() {
  local res; res=$(mktemp)

  run -e --no-check-anchors https://docs.airbyte.io | grep -v '<link>' | grep -E 'HTTP 404' > $res || true
  if grep -q 404 $res; then
    cat $res
    error "Found broken links"
  fi
}

function main() {
  assert_root

  local cmd; cmd=$1; shift || error "Missing command"

  "$cmd" "$@"
}

main "$@"
