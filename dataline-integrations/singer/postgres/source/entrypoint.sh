#!/bin/bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

function main() {
  jq '.filter_dbs = .dbname' /data/job/tap_config.json > /data/job/tap_config_tmp.json
  mv /data/job/tap_config_tmp.json /data/job/tap_config.json
  tap-postgres "$@"
}

main "$@"
