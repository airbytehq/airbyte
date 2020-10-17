#!/bin/bash

set -e

function echo_err() {
  echo >&2 "$@"
}

function main() {
  # Singer's discovery is what we currently use to check connection
  if [[ "$*" =~ .*"--discover".* ]]; then
    echo_err "Checking connection..."
    python3 /singer/check_connection.py "$@"
  elif [[ "$*" =~ .*"--spec".* ]]; then
    echo_err "Getting spec..."
    cat /singer/spec.json
  else
    echo_err "Running sync..."
    target-postgres "$@"
  fi
}

main "$@"
