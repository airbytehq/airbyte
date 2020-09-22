#!/bin/bash
function echo_err() {
  echo >&2 "$@"
}

function main() {
  # Singer's discovery is what we currently use to check connection
  if [[ "$*" =~ .*"--discover".* ]]; then
    echo "INFO Checking connection..."
    python3 /check_connection.py "$@"
  else
    echo "INFO Running sync..."
    target-postgres "$@"
  fi
}

main "$@"
