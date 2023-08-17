#!/usr/bin/env bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

# todo: make it easy to select source or destination and validate based on selection by adding an integration type env variable.
function main() {
  nohup bash -c "socat tcp-listen:9000,reuseaddr,fork \"exec:printf \'HTTP/1.0 200 OK\r\n\r\n\'\" &";
  cat <&0 | /airbyte/bin/"$APPLICATION" "$@"
}

main "$@"
