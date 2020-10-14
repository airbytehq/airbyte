#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

_get_rule_base() {
  local rule; rule=$(echo "$1" | tr -s / :)
  echo ":$rule"
}

_check_tag_exists() {
  DOCKER_CLI_EXPERIMENTAL=enabled docker manifest inspect "$1" > /dev/null
}

cmd_build() {
  local path=$1

  echo "Building $path"
  ./gradlew "$(_get_rule_base "$path"):clean"
  ./gradlew "$(_get_rule_base "$path"):integrationTest"
}

cmd_publish() {
  local path=$1

  cmd_build "$path"

  local image_name; image_name=$(_get_docker_image_name "$path"/Dockerfile)
  local image_version; image_version=$(_get_docker_image_version "$path"/Dockerfile)
  local versioned_image=$image_name:$image_version
  local latest_image=$image_name:latest

  docker tag $image_name $versioned_image
  docker tag $image_name $latest_image

  if _check_tag_exists $versioned_image; then
    error "You're trying to push an image_version that was already released ($versioned_image). Make sure you bump it up."
  fi

  echo "Publishing new image_version ($versioned_image)"
  docker push $versioned_image
  docker push $latest_image
}

USAGE="

Usage: $(basename $0) <build|publish> <integration_root_path>
"

main() {
  assert_root

  local cmd=$1
  shift || error "Missing cmd $USAGE"
  local path=$1
  shift || error "Missing target (root path of integration) $USAGE"

  [ -d "$path" ] || error "Path must be the root path of the integration"

  cmd_"$cmd" "$path"
}

main "$@"
