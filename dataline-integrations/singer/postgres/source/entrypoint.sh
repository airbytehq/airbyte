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
  jq '.filter_dbs = .dbname' tap_config.json > tap_config_tmp.json
  mv tap_config_tmp.json tap_config.json
  tap-postgres "$@"
}

main "$@"
