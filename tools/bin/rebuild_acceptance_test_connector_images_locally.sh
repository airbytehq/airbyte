#!/usr/bin/env bash

# When running acceptance tests, this often manifests as a conenctor sometimes getting stuck for no discernable reason.
# This script allows building all of the connector images used in the acceptance tests.
# We will need to update this file if the versions used for source-e2e-test and destination-e2e-test change before we start publishing ARM images.

set -e

. tools/lib/lib.sh

assert_root

unset SUB_BUILD

LATEST_POSTGRES_SOURCE=$(grep -A1 'airbyte/source-postgres' ./airbyte-config/init/src/main/resources/seed/source_definitions.yaml | grep -v postgres | cut -d ' '  -f 4)
LATEST_POSTGRES_DESTINATION=$(grep -A1 'airbyte/destination-postgres' ./airbyte-config/init/src/main/resources/seed/destination_definitions.yaml | grep -v postgres | cut -d ' '  -f 4)

git checkout master && ./gradlew clean :airbyte-integrations:connectors:source-postgres:build -x test && docker tag airbyte/source-postgres:dev airbyte/source-postgres:"$LATEST_POSTGRES_SOURCE"
git checkout master && ./gradlew clean :airbyte-integrations:connectors:destination-postgres:build -x test && docker tag airbyte/destination-postgres:dev airbyte/destination-postgres:"$LATEST_POSTGRES_DESTINATION"
git checkout 464c485b94c9f023b4c5929610f60a6b53bf657b && ./gradlew clean :airbyte-integrations:connectors:source-e2e-test:build -x test && docker tag airbyte/source-e2e-test:dev airbyte/source-e2e-test:0.1.1
git checkout 464c485b94c9f023b4c5929610f60a6b53bf657b && ./gradlew clean :airbyte-integrations:connectors:destination-e2e-test:build -x test && docker tag airbyte/destination-e2e-test:dev airbyte/destination-e2e-test:0.1.1
