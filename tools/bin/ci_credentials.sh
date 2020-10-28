#!/usr/bin/env bash

set -e

mkdir airbyte-integrations/connectors/destination-bigquery/secrets/
lecho "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/destination-bigquery/secrets/credentials.json

mkdir airbyte-integrations/connectors/source-stripe-singer/secrets/
echo "$STRIPE_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/source-stripe-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-github-singer/secrets/
# pull sample config. add in the access key. write to secrets.
jq --arg v "$GH_INTEGRATION_TEST_CREDS" '.access_token = $v' airbyte-integrations/connectors/source-github-singer/config.sample.json > airbyte-integrations/connectors/source-github-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-salesforce-singer/secrets/
echo "$SALESFORCE_INTEGRATION_TESTS_CREDS" > airbyte-integrations/connectors/source-salesforce-singer/secrets/config.json
