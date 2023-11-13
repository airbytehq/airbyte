#!/usr/bin/env bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

# This is to heartbeat with the destination connector
# Starts a lightweight HTTP server that listens on port 9000. When a client connects to this server,
# it immediately responds with a minimal HTTP response header of "HTTP/1.0 200 OK", indicating a successful request
function main() {
  nohup bash -c "socat tcp-listen:9000,reuseaddr,fork \"exec:printf \'HTTP/1.0 200 OK\r\n\r\n\'\" &";
  cat <&0 | /airbyte/bin/"$APPLICATION" "$@"
}

main "$@"
