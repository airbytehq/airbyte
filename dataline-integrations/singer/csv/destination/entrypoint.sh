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

function main() {
  echo "hi!"
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
    *)
      error "Unknown option: $1"
      shift
      ;;
    esac
  done

  echo "ARGS"
  echo $ARGS
  if [[ "$ARGS" =~ .*"--discover".* ]]; then
    echo2 "Discovering..."
    DESTINATION_PATH=$(jq -r '.destination_path' $PROCESSED_CONFIG_FILE)
    if [[ ! -d "$DESTINATION_PATH" && ! -L "$DESTINATION_PATH" ]] ; then
      echo2 "Could not access path $DESTINATION_PATH" && exit 1
    fi
    # If connection check is successful write a fake catalog for the discovery worker to find
    echo '{"streams":[]}' > "catalog.json"
  else
    target-csv $ARGS
  fi
}

main "$@"
