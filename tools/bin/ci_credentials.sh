#!/usr/bin/env bash

set -e

CONNECTOR_BASE=airbyte-integrations/connectors

function install_secret() {
  local path; path=$1/secrets
  local filename; filename=$2
  local value; value=$3

  mkdir "$path"
  echo "$value" > "$path/secrets/$filename"
}

# BigQuery Credentials
install_secret $CONNECTOR_BASE/bigquery/_deprecated-destination-singer/ credentials.json "$BIGQUERY_INTEGRATION_TEST_CREDS"
install_secret $CONNECTOR_BASE/bigquery/destination/ credentials.json "$BIGQUERY_INTEGRATION_TEST_CREDS"

# Stripe Credentials
install_secret $CONNECTOR_BASE/stripe/_deprecated-source-singer/ config.json "$STRIPE_INTEGRATION_TEST_CREDS"
install_secret $CONNECTOR_BASE/stripe/source-singer/ config.json "$STRIPE_INTEGRATION_TEST_CREDS"
