#!/usr/bin/env bash

set -e

# launches integration test workflows for master builds

# todo: check if existing things already run for these on master
# todo: report status of jobs somewhere

if [[ -z "$GITHUB_TOKEN" ]] ; then
  echo "GITHUB_TOKEN not set..."
  exit 1
fi

echo "TODO..."
