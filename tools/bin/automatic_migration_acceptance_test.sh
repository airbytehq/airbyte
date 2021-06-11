#!/usr/bin/env bash
set -e

. tools/lib/lib.sh

assert_root

echo "Starting app for automaticMigrationAcceptanceTest"


ENV_VERSION=$(grep VERSION .env | xargs)
ENV_VERSION=${ENV_VERSION#*=}
echo "Running AutomaticMigrationAcceptanceTest test via gradle"
MIGRATION_TEST_VERSION=$ENV_VERSION ./gradlew --no-daemon :airbyte-tests:automaticMigrationAcceptanceTest --rerun-tasks --scan -i