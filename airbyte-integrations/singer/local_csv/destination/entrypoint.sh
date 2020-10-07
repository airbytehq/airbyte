#!/bin/bash

set -e

PROCESSED_CONFIG_FILE="processed_config.json"

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

function canAccessLocal() {
  if [[ ! -d "/local" && ! -L "/local" ]] ; then
    echo2 "Could not access path /local" && exit 1
  fi
}

function mkdirOrThrow() {
  mkdir -p "$@"
  if [ $? -ne 0 ] ; then
    echo2 "Could not create directory $@" && exit 1
  fi
}

function main() {
  ARGS=
  while [ $# -ne 0 ]; do
    case "$1" in
    -a | --discover)
      ARGS="$ARGS --discover"
      shift 1
      ;;
    -b | --config)
      jq '.destination_path = "/local/" + .destination_path' $2 > $PROCESSED_CONFIG_FILE
      ARGS="$ARGS --config $PROCESSED_CONFIG_FILE"
      shift 2
      ;;
    --spec)
      ARGS="$ARGS --spec"
      shift
      ;;
    *)
      error "Unknown option: $1"
      shift
      ;;
    esac
  done

  canAccessLocal
  DESTINATION_PATH=$(jq -r '.destination_path' $PROCESSED_CONFIG_FILE)
  mkdirOrThrow "$DESTINATION_PATH"
  if [[ "$ARGS" =~ .*"--discover".* ]]; then
    echo2 "Discovering..."
    # If connection check is successful write a fake catalog for the discovery worker to find
    echo '{"streams":[]}'
  elif [[ "$ARGS" =~ .*"--spec".* ]]; then
    cat /singer/spec.json
  else
    target-csv $ARGS
  fi
}

main "$@"
