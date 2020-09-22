#!/bin/bash
function echo_err() {
  echo >&2 "$@"
}

function main() {
  # Singer's discovery is what we currently use to check connection
  if [[ "$*" =~ .*"--discover".* ]]; then
    echo "Checking connection..."
    python3 /check_connection.py "$@"
  else
    echo "Running sync..."
    target-postgres "$@"
  fi
}

main "$@"
