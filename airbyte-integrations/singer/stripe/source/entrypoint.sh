#!/usr/bin/env bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

# TODO: replace with more general version
# hacky version that expects ordering of args "--config config.json --discover"
function check_connection() {

  if [[ "$1" == "--config" ]]; then
    echo2 "Config provided, running check connection."
    CONFIG_FILE=$2
    echo2 "Using config file \"$CONFIG_FILE\""
    STRIPE_KEY=$(jq -r ".client_secret" "$CONFIG_FILE")
    OUTPUT=$(curl https://api.stripe.com/v1/customers -u "$STRIPE_KEY:")

    if [[ "$OUTPUT" =~ .*"Invalid API Key".* ]]; then
      echo2 "Connection check failed."
      exit 2
    else
      echo2 "Connection checked and valid."
    fi
  else
    echo2 "No config, not running check_connection."
    exit 3
  fi
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
      ARGS="$ARGS --config $2"
      shift 2
      ;;
    --state)
      ARGS="$ARGS --state $2"
      shift 2
      ;;
    --properties)
      ARGS="$ARGS --catalog $2"
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

  echo2 "ARGS"
  echo2 $ARGS
  if [[ "$ARGS" =~ .*"--discover".* ]]; then
    echo2 "discover"
    check_connection $ARGS
    tap-stripe $ARGS
  elif [[ "$ARGS" =~ .*"--spec".* ]]; then
    echo2 'spec'
    tr -d '\n' < /singer/spec.json
  else
    echo2 "sync"
    tap-stripe $ARGS
  fi
}

main "$@"
