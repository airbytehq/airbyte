#!/bin/bash

function check_connection() {
  local CONFIG_FILE_PATH=
  while test $# -gt 0; do
    case "$1" in
    --config)
      shift
      CONFIG_FILE_PATH="$1"
      python3 /check_connection.py "$CONFIG_FILE_PATH"
      if [ $? -gt 0 ]; then
        exit 1
      else
        # If connection check is successful write a fake catalog for the discovery worker to find
        echo '{"streams":[]}' > catalog.json
      fi
      ;;
    esac
    shift
  done
}

function echo_err(){
  >&2 echo "$@"
}

function main() {
  # Singer's discovery is what we currently use to check connection
  if [[ "$*" =~ .*"--discover".* ]]; then
   echo_err "Checking connection..."
    check_connection "$@"
  else
    echo_err "Running sync..."
    target-postgres "$@"
  fi
}

main "$@"
