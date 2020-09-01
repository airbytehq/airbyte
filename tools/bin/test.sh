#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# Detach so we can run subsequent commands
VERSION=dev docker-compose up -d
trap "docker-compose stop" EXIT

echo "Waiting for services to begin"
sleep 10 # TODO what's a better way to wait on this

echo "Running e2e tests via gradle"
./gradlew :dataline-acceptance-tests:acceptanceTests
