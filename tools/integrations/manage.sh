#!/usr/bin/env sh

set -e

. tools/lib/lib.sh

DOCKER_ORG=${DOCKER_ORG:-dataline}

get_name() {
  local name=$(dirname $1 | sed "s/^dataline-integrations/integration/" | tr / -)
  echo "${DOCKER_ORG}/$name"
}

cmd_build() {
  local path=$1

  echo "Building $path"
  docker build -f "$path" -t "$(get_name $path)" "$(dirname "$path")" | grep "Successfully tagged"
}

cmd_publish() {
  local name=$(get_name "$1")

  echo "Pushing $name"
  docker push "$name"
}

main() {
  assert_root

  local cmd=$1
  shift || error "Missing cmd"
  local path=$1
  shift || error "Missing target (root path of integration or 'all')"

  if [[ $path == "all" ]]; then
    for path in $(find dataline-integrations -iname "Dockerfile" -type f); do
      cmd_$cmd $path
    done
  else
    cmd_$cmd $path
  fi
}

main "$@"
