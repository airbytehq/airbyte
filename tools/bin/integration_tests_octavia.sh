#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# Detach so we can run subsequent commands
VERSION=dev TRACKING_STRATEGY=logging BASIC_AUTH_USERNAME="" BASIC_AUTH_PASSWORD="" docker compose up -d

# Sometimes source/dest containers using airbyte volumes survive shutdown, which need to be killed in order to shut down properly.
shutdown_cmd="docker compose down -v || docker kill \$(docker ps -a -f volume=airbyte_workspace -f volume=airbyte_data -f volume=airbyte_db -q) && docker compose down -v"
trap "echo 'docker compose logs:' && docker compose logs -t --tail 1000 && $shutdown_cmd" EXIT

echo "Waiting for services to begin"
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8000/api/v1/health)" != "200" ]]; do echo "Waiting for docker deployment.."; sleep 5; done

echo "Running integration tests via gradle"
SUB_BUILD=OCTAVIA_CLI ./gradlew :octavia-cli:integrationTest --rerun-tasks --scan
