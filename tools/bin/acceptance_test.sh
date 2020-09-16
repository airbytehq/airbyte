#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# Detach so we can run subsequent commands
VERSION=dev docker-compose up -d
trap "echo 'docker-compose logs: \n\n' && docker-compose logs -t --tail 150 && docker-compose down" EXIT

echo "Waiting for services to begin"
sleep 10 # TODO need a better way to wait

echo "Running e2e tests via gradle"
./gradlew :dataline-tests:acceptanceTests
