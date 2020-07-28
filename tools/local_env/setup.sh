#!/usr/bin/env bash

set -e

function _error() {
  echo "$@"
  exit 1
}

function main() {
  [[ -e .root ]] || _error "Must run from root"

  git remote add oss https://github.com/datalineio/public.git
}

main "$@"
