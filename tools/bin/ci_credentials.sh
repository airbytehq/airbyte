#!/usr/bin/env bash

set -e

mkdir dataline-integrations/singer/bigquery/destination/config
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > dataline-integrations/singer/bigquery/destination/config/credentials.json

mkdir dataline-integrations/singer/stripe/source/config
echo "$STRIPE_INTEGRATION_TEST_CREDS" > dataline-integrations/singer/stripe/source/config/config.json
