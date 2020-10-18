#!/usr/bin/env bash

set -e

function install_secret() {
  local secrets_path; secrets_path=$1/secrets
  local filename; filename=$2
  local value; value=$3

  mkdir "$secrets_path"
  echo "$value" > "$secrets_path/$filename"
}

# BigQuery Credentials
install_secret $CONNECTOR_BASE/bigquery/_deprecated-destination-singer credentials.json "$BIGQUERY_INTEGRATION_TEST_CREDS"
install_secret $CONNECTOR_BASE/bigquery/destination credentials.json "$BIGQUERY_INTEGRATION_TEST_CREDS"

# Stripe Credentials
install_secret $CONNECTOR_BASE/stripe/_deprecated-source-singer config.json "$STRIPE_INTEGRATION_TEST_CREDS"
install_secret $CONNECTOR_BASE/stripe/source-singer config.json "$STRIPE_INTEGRATION_TEST_CREDS"
