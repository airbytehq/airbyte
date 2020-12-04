#!/usr/bin/env bash

set -e

mkdir airbyte-integrations/connectors/destination-bigquery/secrets/
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/destination-bigquery/secrets/credentials.json

mkdir airbyte-integrations/connectors/source-stripe-singer/secrets/
echo "$STRIPE_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/source-stripe-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-github-singer/secrets/
# pull sample config. add in the access key. write to secrets.
jq --arg v "$GH_INTEGRATION_TEST_CREDS" '.access_token = $v' airbyte-integrations/connectors/source-github-singer/config.sample.json > airbyte-integrations/connectors/source-github-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-googleanalytics-singer/secrets/
echo "$GOOGLE_ANALYTICS_TEST_CREDS" > airbyte-integrations/connectors/source-googleanalytics-singer/secrets/config.json
echo "$GOOGLE_ANALYTICS_TEST_TRACKING_ID" > airbyte-integrations/connectors/source-googleanalytics-singer/secrets/tracker.txt

mkdir airbyte-integrations/connectors/source-salesforce-singer/secrets/
echo "$SALESFORCE_INTEGRATION_TESTS_CREDS" > airbyte-integrations/connectors/source-salesforce-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-hubspot-singer/secrets/
echo "$HUBSPOT_INTEGRATION_TESTS_CREDS" > airbyte-integrations/connectors/source-hubspot-singer/secrets/config.json

mkdir airbyte-integrations/connectors/source-google-sheets/secrets
echo "$GSHEETS_INTEGRATION_TESTS_CREDS" > airbyte-integrations/connectors/source-google-sheets/secrets/creds.json

mkdir airbyte-integrations/connectors/destination-snowflake/secrets
echo "$SNOWFLAKE_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/destination-snowflake/secrets/config.json

mkdir airbyte-integrations/connectors/source-google-adwords-singer/secrets
echo "$ADWORDS_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/source-google-adwords-singer/secrets/config.json

FB_SECRETS_DIR=airbyte-integrations/connectors/source-facebook-marketing-api-singer/secrets
mkdir $FB_SECRETS_DIR
echo "$FACEBOOK_MARKETING_API_TEST_INTEGRATION_CREDS" > "${FB_SECRETS_DIR}/config.json"

MKTO_SECRETS_DIR=airbyte-integrations/connectors/source-marketo-singer/secrets
mkdir $MKTO_SECRETS_DIR
echo "$SOURCE_MARKETO_SINGER_INTEGRATION_TEST_CONFIG" > "${MKTO_SECRETS_DIR}/config.json"


mkdir airbyte-integrations/connectors/source-shopify-singer/secrets
echo "$SHOPIFY_INTEGRATION_TEST_CREDS" > airbyte-integrations/connectors/source-shopify-singer/secrets/config.json

SOURCEFILE_DIR=airbyte-integrations/connectors/source-file/secrets
mkdir $SOURCEFILE_DIR
echo "$BIGQUERY_INTEGRATION_TEST_CREDS" > "${SOURCEFILE_DIR}/gcs.json"
echo "$AWS_S3_INTEGRATION_TEST_CREDS" > "${SOURCEFILE_DIR}/aws.json"

REDSHIFT_DIR=airbyte-integrations/connectors/source-redshift/secrets
mkdir $REDSHIFT_DIR
echo "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS" > "${REDSHIFT_DIR}/config.json"

REDSHIFT_DIR=airbyte-integrations/connectors/destination-redshift/secrets
mkdir $REDSHIFT_DIR
echo "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS" > "${REDSHIFT_DIR}/config.json"

MAILCHIMP_SECRETS_DIR=airbyte-integrations/connectors/source-mailchimp/secrets
mkdir $MAILCHIMP_SECRETS_DIR
echo "$MAILCHIMP_TEST_CREDS" > "${MAILCHIMP_SECRETS_DIR}/config.json"

RECURLY_SECRETS_DIR=airbyte-integrations/connectors/source-recurly/secrets
mkdir $RECURLY_SECRETS_DIR
echo "$SOURCE_RECURLY_INTEGRATION_TEST_CREDS" > "${RECURLY_SECRETS_DIR}/config.json"

FRESHDESK_SECRETS_DIR=airbyte-integrations/connectors/source-freshdesk/secrets
mkdir $FRESHDESK_SECRETS_DIR
echo "$FRESHDESK_TEST_CREDS" > "${FRESHDESK_SECRETS_DIR}/config.json"

TWILIO_SECRETS_DIR=airbyte-integrations/connectors/source-twilio-singer/secrets
mkdir $TWILIO_SECRETS_DIR
echo "$TWILIO_TEST_CREDS" > "${TWILIO_SECRETS_DIR}/config.json"

BRAINTREE_SECRETS_DIR=airbyte-integrations/connectors/source-braintree-singer/secrets
mkdir $BRAINTREE_SECRETS_DIR
echo "$BRAINTREE_TEST_CREDS" > "${BRAINTREE_SECRETS_DIR}/config.json"
