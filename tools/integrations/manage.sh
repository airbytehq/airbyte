#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

_get_rule_base() {
  local rule=$(echo "$1" | tr -s / :)
  echo ":$rule"
}

_get_image() {
  local path=$1
  ./gradlew "$(_get_rule_base "$path"):imageName" | grep IMAGE | cut -d ' ' -f 2
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

  local dev_image=$(_get_image "$path")
  local versioned_image=${dev_image%:*}:$(_get_docker_version "$path"/Dockerfile)
  local latest_image=${dev_image%:*}:latest

  docker tag $dev_image $versioned_image
  docker tag $dev_image $latest_image

  if _check_tag_exists $versioned_image; then
    error "You're trying to push an version that was already released ($versioned_image). Make sure you bump it up."
  fi

  echo "Publishing new version ($versioned_image)"
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
