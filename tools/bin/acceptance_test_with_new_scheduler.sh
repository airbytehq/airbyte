#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# Detach so we can run subsequent commands
VERSION=dev TRACKING_STRATEGY=logging NEW_SCHEDULER=true docker-compose up -d
trap "echo 'docker-compose logs:' && docker-compose logs -t --tail 1000 && docker-compose down -v" EXIT

echo "Waiting for services to begin"
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8000/api/v1/health)" != "200" ]]; do echo "Waiting for docker deployment.."; sleep 5; done

echo "Running e2e tests via gradle"
SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true ./gradlew :airbyte-tests:acceptanceTests --rerun-tasks --scan
