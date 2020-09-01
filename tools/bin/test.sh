#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."
VERSION=dev docker-compose up -d
trap "docker-compose stop" EXIT

echo "Running e2e tests via gradle"
echo "Sleeping"
sleep 10 # TODO what's a better way to wait on this
./gradlew :dataline-acceptance-tests:acceptanceTests
