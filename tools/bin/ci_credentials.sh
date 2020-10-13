#!/usr/bin/env bash

set -e

mkdir airbyte-integrations/singer/bigquery/destination/config
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/singer/bigquery/destination/config/credentials.json
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/bigquery-destination/config/credentials.json

mkdir airbyte-integrations/singer/stripe/source/config
echo "$STRIPE_INTEGRATION_TEST_CREDS" > airbyte-integrations/singer/stripe/source/config/config.json
