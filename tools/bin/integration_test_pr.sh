#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

./gradlew --no-daemon --scan -x generateProtocolClassFiles \
  :airbyte-integrations:connectors:destination-bigquery:integrationTest \
  :airbyte-integrations:connectors:destination-postgres:integrationTest \
  :airbyte-integrations:connectors:destination-csv:integrationTest \
  :airbyte-integrations:connectors:source-postgres:integrationTest \
  :airbyte-integrations:connectors:source-stripe-singer:integrationTest \
  :airbyte-integrations:connectors:source-exchangeratesapi-singer:integrationTest
