#!/usr/bin/env bash

. tools/lib/lib.sh

set -e

function write_standard_creds() {
  local connector_name=$1
  local creds=$2
  local cred_filename=${3:-config.json}

  [ -z "$connector_name" ] && error "Empty connector name"
  [ -z "$creds" ] && error "Creds not set for $connector_name"

  local secrets_dir="airbyte-integrations/connectors/${connector_name}/secrets"
  mkdir -p "$secrets_dir"
  echo "$creds" > "${secrets_dir}/${cred_filename}"
}

write_standard_creds destination-bigquery "$BIGQUERY_INTEGRATION_TEST_CREDS" "credentials.json"
write_standard_creds destination-snowflake "$SNOWFLAKE_INTEGRATION_TEST_CREDS"
write_standard_creds destination-redshift "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS"

write_standard_creds source-file "$BIGQUERY_INTEGRATION_TEST_CREDS" "gcs.json"
write_standard_creds source-braintree-singer "$BRAINTREE_TEST_CREDS"
write_standard_creds source-file "$AWS_S3_INTEGRATION_TEST_CREDS" "aws.json"
write_standard_creds source-freshdesk "$FRESHDESK_TEST_CREDS"
write_standard_creds source-facebook-marketing-api-singer "$FACEBOOK_MARKETING_API_TEST_INTEGRATION_CREDS"
# pull sample config. add in the access key. write to secrets.
GH_CREDS=$(jq --arg v "$GH_INTEGRATION_TEST_CREDS" '.access_token = $v' airbyte-integrations/connectors/source-github-singer/config.sample.json)
write_standard_creds source-github-singer "$GH_CREDS"
write_standard_creds source-google-adwords-singer "$ADWORDS_INTEGRATION_TEST_CREDS"
write_standard_creds source-googleanalytics-singer "$GOOGLE_ANALYTICS_TEST_CREDS"
write_standard_creds source-googleanalytics-singer "$GOOGLE_ANALYTICS_TEST_TRACKING_ID" "tracker.txt"
write_standard_creds source-google-sheets "$GSHEETS_INTEGRATION_TESTS_CREDS" "creds.json"
write_standard_creds source-greenhouse "$GREENHOUSE_TEST_CREDS"
write_standard_creds source-hubspot-singer "$HUBSPOT_INTEGRATION_TESTS_CREDS"
write_standard_creds source-intercom-singer "$INTERCOM_INTEGRATION_TEST_CREDS"
write_standard_creds source-jira "$JIRA_INTEGRATION_TEST_CREDS"
write_standard_creds source-mailchimp "$MAILCHIMP_TEST_CREDS"
write_standard_creds source-marketo-singer "$SOURCE_MARKETO_SINGER_INTEGRATION_TEST_CONFIG"
write_standard_creds source-recurly "$SOURCE_RECURLY_INTEGRATION_TEST_CREDS"
write_standard_creds source-redshift "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS"
write_standard_creds source-salesforce-singer "$SALESFORCE_INTEGRATION_TESTS_CREDS"
write_standard_creds source-sendgrid "$SENDGRID_INTEGRATION_TEST_CREDS"
write_standard_creds source-shopify-singer "$SHOPIFY_INTEGRATION_TEST_CREDS"
write_standard_creds source-slack-singer "$SLACK_TEST_CREDS"
write_standard_creds source-stripe-singer "$STRIPE_INTEGRATION_TEST_CREDS"
write_standard_creds source-twilio-singer "$TWILIO_TEST_CREDS"
write_standard_creds source-zendesk-singer "$ZENDESK_SECRETS_CREDS"
