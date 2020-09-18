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
  ARGS=
  while [ $# -ne 0 ]; do
    case "$1" in
    --discover)
      ARGS="$ARGS --discover"
      shift 1
      ;;
    --config)
      jq '.filter_dbs = .dbname' $2 > $PROCESSED_CONFIG_FILE
      ARGS="$ARGS --config $PROCESSED_CONFIG_FILE"
      shift 2
      ;;
    --state)
      ARGS="$ARGS --state $2"
      shift 2
      ;;
    --catalog)
      ARGS="$ARGS --catalog $2"
      shift 2
      ;;

    --properties)
      ARGS="$ARGS --properties $2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      shift
      ;;
    esac
  done

  tap-postgres $ARGS
}

main "$@"
