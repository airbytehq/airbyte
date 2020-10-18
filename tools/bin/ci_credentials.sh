#!/usr/bin/env bash

set -e

mkdir airbyte-integrations/singer/bigquery/destination/secrets
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/singer/bigquery/destination/secrets/credentials.json

mkdir airbyte-integrations/bigquery-destination/secrets
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/bigquery-destination/secrets/credentials.json

mkdir airbyte-integrations/singer/stripe/source/secrets
echo "$STRIPE_INTEGRATION_TEST_CREDS" > airbyte-integrations/singer/stripe/source/secrets/config.json

mkdir airbyte-integrations/singer/stripe_abprotocol/source/secrets
echo "$STRIPE_INTEGRATION_TEST_CREDS" > airbyte-integrations/singer/stripe_abprotocol/source/secrets/config.json
