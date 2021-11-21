#!/usr/bin/env bash

. tools/lib/lib.sh
. tools/lib/gcp-token.sh

set -e

# all secrets will be loaded if the second argument is not present
CONNECTOR_FULLNAME=${1:-all}
CONNECTOR_NAME=`echo ${CONNECTOR_FULLNAME} | rev | cut -d'/' -f1 | rev`

GSM_SCOPES="https://www.googleapis.com/auth/cloud-platform"

# If a secret is available in both Github and GSM, then the GSM secret is used, otherwise Github.

declare -A SECRET_MAP


function read_secrets() {
  local connector_name=$1
  local creds=$2
  local cred_filename=${3:-config.json}
  local secrets_provider_name=${4:-github}

  [ -z "$connector_name" ] && error "Empty connector name"
  [ -z "$creds" ] && echo "!!!!!Creds not set for the connector $connector_name from ${secrets_provider_name}"

  if [[ $CONNECTOR_NAME != "all" && ${connector_name} != ${CONNECTOR_NAME} ]]; then
    return 0
  fi
  local key="${connector_name}#${cred_filename}"
  [[ -z "${creds}" ]] && error "Empty credential for the connector '${key} from ${secrets_provider_name}"
  
  if [ -v SECRET_MAP[${key}] ]; then
    echo "The connector '${key}' was added before"
    return 0
  fi
  echo "register the secret ${key} from ${secrets_provider_name}"
  SECRET_MAP[${key}]="${creds}"
  return 0
}

function write_secret_to_disk() {
  local connector_name=$1
  local cred_filename=$2
  local creds=$3
  if jq -e . >/dev/null 2>&1 <<< "${creds}"; then
    echo "Parsed JSON for '${connector_name}' => ${cred_filename} successfully"
  else
    error "Failed to parse JSON for '${connector_name}' => ${cred_filename}"
  fi

  if [ "$connector_name" = "base-normalization" ]; then
    local secrets_dir="airbyte-integrations/bases/${connector_name}/secrets"
  else
    local secrets_dir="airbyte-integrations/connectors/${connector_name}/secrets"
  fi
  mkdir -p "$secrets_dir"
  echo "Saved a secret => ${secrets_dir}/${cred_filename}"
  echo "$creds" > "${secrets_dir}/${cred_filename}"
}

function write_all_secrets() {
  for key in "${!SECRET_MAP[@]}"; do
    local connector_name=$(echo ${key} | cut -d'#' -f1)
    local cred_filename=$(echo ${key} | cut -d'#' -f2)
    local creds=${SECRET_MAP[${key}]}
    write_secret_to_disk ${connector_name} ${cred_filename} "${creds}" 
    
  done
  return 0
}


function export_github_secrets(){
  # We expect that all secrets injected from github are available in an env variable `SECRETS_JSON`
  local pairs=`echo ${GITHUB_PROVIDED_SECRETS_JSON} | jq -c 'keys[] as $k | {"name": $k, "value": .[$k]} | @base64'`
  while read row; do
    pair=$(echo "${row}" | tr -d '"' | base64 -d)
    local key=$(echo ${pair} | jq -r .name)  
    local value=$(echo ${pair} | jq -r .value)
    if [[ "$key" == *"_CREDS"* ]]; then
      declare -gxr "${key}"="$(echo ${value})"
    fi
  done <<< ${pairs}
  unset GITHUB_PROVIDED_SECRETS_JSON
}

function export_gsm_secrets(){
  local config_file=`mktemp`
  echo "${GCP_GSM_CREDENTIALS}" > ${config_file}
  local access_token=$(get_gcp_access_token "${config_file}" "${GSM_SCOPES}")
  local project_id=$(parse_project_id "${config_file}")
  rm ${config_file}

  # docs: https://cloud.google.com/secret-manager/docs/filtering#api
  local filter="name:SECRET_"
  [[ ${CONNECTOR_NAME} != "all" ]] && filter="${filter} AND labels.connector=${CONNECTOR_NAME}"
  local uri="https://secretmanager.googleapis.com/v1/projects/${project_id}/secrets"
  local next_token=''
  while true; do
    local data=$(curl -s --get --fail "${uri}" \
      --data-urlencode "filter=${filter}" \
      --data-urlencode "pageToken=${next_token}" \
      --header "authorization: Bearer ${access_token}" \
      --header "content-type: application/json" \
      --header "x-goog-user-project: ${project_id}")
    [[ -z ${data} ]] && error "Can't load secret for connector ${CONNECTOR_NAME}"
    # GSM returns an empty JSON object if secrets are not found.
    # It breaks JSON parsing by the 'jq' utility. The simplest fix is response normalization 
    [[ ${data} == "{}" ]] && data='{"secrets": []}'

    for row in $(echo "${data}" | jq -r '.secrets[] | @base64'); do
      local secret_info=$(echo ${row} | base64 --decode)
      local secret_name=$(echo ${secret_info}| jq -r .name)
      local label_filename=$(echo ${secret_info}| jq -r '.labels.filename // "config"')
      local label_connectors=$(echo ${secret_info}| jq -r '.labels.connector // ""')

      # skip secrets without the label "connector"
      [[ -z ${label_connectors} ]] && continue
      if [[ "$label_connectors" != *"${CONNECTOR_NAME}"* ]]; then
        echo "Not found ${CONNECTOR_NAME} info into the label 'connector' of the secret ${secret_name}"
        continue
      fi

      # all secret file names should be finished with ".json"
      # but '.' cant be used in google, so we append it
      local filename="${label_filename}.json"
      echo "found the Google secret of ${label_connectors}: ${secret_name} => ${filename}"
      local secret_uri="https://secretmanager.googleapis.com/v1/${secret_name}/versions/latest:access"
      local secret_data=$(curl -s --get --fail "${secret_uri}" \
        --header "authorization: Bearer ${access_token}" \
        --header "content-type: application/json" \
        --header "x-goog-user-project: ${project_id}")
      [[ -z ${secret_data} ]] && error "Can't load secrets' list"

      secret_data=$(echo ${secret_data} | jq -r '.payload.data // ""' | base64 -d)
      read_secrets "${CONNECTOR_NAME}" "${secret_data}" "${filename}" "gsm"
    done
    next_token=`echo ${data} | jq -r '.nextPageToken // ""'`
    [[ -z ${next_token} ]] && break
  done
  return 0
}

export_gsm_secrets
export_github_secrets



# Please maintain this organisation and alphabetise.
read_secrets destination-bigquery "$BIGQUERY_INTEGRATION_TEST_CREDS" "credentials.json"
read_secrets destination-bigquery-denormalized "$BIGQUERY_DENORMALIZED_INTEGRATION_TEST_CREDS" "credentials.json"
read_secrets destination-databricks "$DESTINATION_DATABRICKS_CREDS"
read_secrets destination-gcs "$DESTINATION_GCS_CREDS"
read_secrets destination-kvdb "$DESTINATION_KVDB_TEST_CREDS"
read_secrets destination-keen "$DESTINATION_KEEN_TEST_CREDS"

read_secrets destination-postgres "$DESTINATION_PUBSUB_TEST_CREDS" "credentials.json"
read_secrets destination-mongodb-strict-encrypt "$MONGODB_TEST_CREDS" "credentials.json"
read_secrets destination-mysql "$MYSQL_SSH_KEY_TEST_CREDS" "ssh-key-config.json"
read_secrets destination-mysql "$MYSQL_SSH_PWD_TEST_CREDS" "ssh-pwd-config.json"
read_secrets destination-pubsub "$DESTINATION_PUBSUB_TEST_CREDS" "credentials.json"
read_secrets destination-redshift "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS"
read_secrets destination-dynamodb "$DESTINATION_DYNAMODB_TEST_CREDS"
read_secrets destination-oracle "$AWS_ORACLE_INTEGRATION_TEST_CREDS"
read_secrets destination-s3 "$DESTINATION_S3_INTEGRATION_TEST_CREDS"
read_secrets destination-azure-blob-storage "$DESTINATION_AZURE_BLOB_CREDS"
read_secrets destination-snowflake "$SNOWFLAKE_GCS_COPY_INTEGRATION_TEST_CREDS" "copy_gcs_config.json"
read_secrets destination-snowflake "$SNOWFLAKE_S3_COPY_INTEGRATION_TEST_CREDS" "copy_s3_config.json"
read_secrets destination-snowflake "$SNOWFLAKE_INTEGRATION_TEST_CREDS" "insert_config.json"

read_secrets base-normalization "$BIGQUERY_INTEGRATION_TEST_CREDS" "bigquery.json"
read_secrets base-normalization "$SNOWFLAKE_INTEGRATION_TEST_CREDS" "snowflake.json"
read_secrets base-normalization "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS" "redshift.json"
read_secrets base-normalization "$AWS_ORACLE_INTEGRATION_TEST_CREDS" "oracle.json"

read_secrets source-airtable "$SOURCE_AIRTABLE_TEST_CREDS"
read_secrets source-amazon-seller-partner "$AMAZON_SELLER_PARTNER_TEST_CREDS"
read_secrets source-amazon-sqs "$SOURCE_AMAZON_SQS_TEST_CREDS"
read_secrets source-amplitude "$AMPLITUDE_INTEGRATION_TEST_CREDS"
read_secrets source-apify-dataset "$APIFY_INTEGRATION_TEST_CREDS"
read_secrets source-amazon-ads "$AMAZON_ADS_TEST_CREDS"
read_secrets source-amplitude "$AMPLITUDE_INTEGRATION_TEST_CREDS"
read_secrets source-asana "$SOURCE_ASANA_TEST_CREDS"
read_secrets source-aws-cloudtrail "$SOURCE_AWS_CLOUDTRAIL_CREDS"
read_secrets source-azure-table "$SOURCE_AZURE_TABLE_CREDS"
read_secrets source-bamboo-hr "$SOURCE_BAMBOO_HR_CREDS"
read_secrets source-bigcommerce "$SOURCE_BIGCOMMERCE_CREDS"
read_secrets source-bigquery "$BIGQUERY_TEST_CREDS" "credentials.json"
read_secrets source-bing-ads "$SOURCE_BING_ADS_CREDS"
read_secrets source-braintree "$BRAINTREE_TEST_CREDS"
read_secrets source-cart "$CART_TEST_CREDS"
read_secrets source-chargebee "$CHARGEBEE_INTEGRATION_TEST_CREDS"
read_secrets source-close-com "$SOURCE_CLOSE_COM_CREDS"
read_secrets source-commercetools "$SOURCE_COMMERCETOOLS_TEST_CREDS"
read_secrets source-confluence "$SOURCE_CONFLUENCE_TEST_CREDS"
read_secrets source-delighted "$SOURCE_DELIGHTED_TEST_CREDS"
read_secrets source-drift "$DRIFT_INTEGRATION_TEST_CREDS"
read_secrets source-dixa "$SOURCE_DIXA_TEST_CREDS"
read_secrets source-exchange-rates "$EXCHANGE_RATES_TEST_CREDS"
read_secrets source-file "$GOOGLE_CLOUD_STORAGE_TEST_CREDS" "gcs.json"
read_secrets source-file "$AWS_S3_INTEGRATION_TEST_CREDS" "aws.json"
read_secrets source-file "$AZURE_STORAGE_INTEGRATION_TEST_CREDS" "azblob.json"
read_secrets source-file "$FILE_SECURE_HTTPS_TEST_CREDS"
read_secrets source-file-secure "$FILE_SECURE_HTTPS_TEST_CREDS"
read_secrets source-freshdesk "$FRESHDESK_TEST_CREDS"
read_secrets source-freshsales "$SOURCE_FRESHSALES_TEST_CREDS"
read_secrets source-freshservice "$SOURCE_FRESHSERVICE_TEST_CREDS"
read_secrets source-facebook-marketing "$FACEBOOK_MARKETING_TEST_INTEGRATION_CREDS"
read_secrets source-facebook-pages "$FACEBOOK_PAGES_INTEGRATION_TEST_CREDS"
read_secrets source-gitlab "$GITLAB_INTEGRATION_TEST_CREDS"
read_secrets source-github "$GH_NATIVE_INTEGRATION_TEST_CREDS"
read_secrets source-google-ads "$GOOGLE_ADS_TEST_CREDS"
read_secrets source-google-analytics-v4 "$GOOGLE_ANALYTICS_V4_TEST_CREDS"
read_secrets source-google-analytics-v4 "$GOOGLE_ANALYTICS_V4_TEST_CREDS_SRV_ACC" "service_config.json"
read_secrets source-google-analytics-v4 "$GOOGLE_ANALYTICS_V4_TEST_CREDS_OLD" "old_config.json"
read_secrets source-google-directory "$GOOGLE_DIRECTORY_TEST_CREDS"
read_secrets source-google-directory "$GOOGLE_DIRECTORY_TEST_CREDS_OAUTH" "config_oauth.json"
read_secrets source-google-search-console "$GOOGLE_SEARCH_CONSOLE_CDK_TEST_CREDS"
read_secrets source-google-search-console "$GOOGLE_SEARCH_CONSOLE_CDK_TEST_CREDS_SRV_ACC" "service_account_config.json"
read_secrets source-google-sheets "$GOOGLE_SHEETS_TESTS_CREDS"
read_secrets source-google-sheets "$GOOGLE_SHEETS_TESTS_CREDS_SRV_ACC" "service_config.json"
read_secrets source-google-sheets "$GOOGLE_SHEETS_TESTS_CREDS_OLD" "old_config.json"
read_secrets source-google-workspace-admin-reports "$GOOGLE_WORKSPACE_ADMIN_REPORTS_TEST_CREDS"
read_secrets source-greenhouse "$GREENHOUSE_TEST_CREDS"
read_secrets source-greenhouse "$GREENHOUSE_TEST_CREDS_LIMITED" "config_users_only.json"
read_secrets source-hubspot "$HUBSPOT_INTEGRATION_TESTS_CREDS"
read_secrets source-hubspot "$HUBSPOT_INTEGRATION_TESTS_CREDS_OAUTH" "config_oauth.json"
read_secrets source-instagram "$INSTAGRAM_INTEGRATION_TESTS_CREDS"
read_secrets source-intercom "$INTERCOM_INTEGRATION_TEST_CREDS"
read_secrets source-intercom "$INTERCOM_INTEGRATION_OAUTH_TEST_CREDS" "config_apikey.json"
read_secrets source-iterable "$ITERABLE_INTEGRATION_TEST_CREDS"
read_secrets source-jira "$JIRA_INTEGRATION_TEST_CREDS"
read_secrets source-klaviyo "$KLAVIYO_TEST_CREDS"
read_secrets source-lemlist "$SOURCE_LEMLIST_TEST_CREDS"
read_secrets source-lever-hiring "$LEVER_HIRING_INTEGRATION_TEST_CREDS"
read_secrets source-looker "$LOOKER_INTEGRATION_TEST_CREDS"
read_secrets source-linnworks "$SOURCE_LINNWORKS_TEST_CREDS"
read_secrets source-mailchimp "$MAILCHIMP_TEST_CREDS"
read_secrets source-marketo "$SOURCE_MARKETO_TEST_CREDS"
read_secrets source-microsoft-teams "$MICROSOFT_TEAMS_TEST_CREDS"
read_secrets source-mixpanel "$MIXPANEL_INTEGRATION_TEST_CREDS"
read_secrets source-monday "$SOURCE_MONDAY_TEST_CREDS"
read_secrets source-mongodb-strict-encrypt "$MONGODB_TEST_CREDS" "credentials.json"
read_secrets source-mongodb-v2 "$MONGODB_TEST_CREDS" "credentials.json"
read_secrets source-mssql "$MSSQL_RDS_TEST_CREDS"
read_secrets source-notion "$SOURCE_NOTION_TEST_CREDS"
read_secrets source-okta "$SOURCE_OKTA_TEST_CREDS"
read_secrets source-onesignal "$SOURCE_ONESIGNAL_TEST_CREDS"
read_secrets source-plaid "$PLAID_INTEGRATION_TEST_CREDS"
read_secrets source-paypal-transaction "$PAYPAL_TRANSACTION_CREDS"
read_secrets source-pinterest "$PINTEREST_TEST_CREDS"
read_secrets source-mysql "$MYSQL_SSH_KEY_TEST_CREDS" "ssh-key-config.json"
read_secrets source-mysql "$MYSQL_SSH_PWD_TEST_CREDS" "ssh-pwd-config.json"
read_secrets source-posthog "$POSTHOG_TEST_CREDS"
read_secrets source-pipedrive "$PIPEDRIVE_INTEGRATION_TESTS_CREDS" "config.json"
read_secrets source-pipedrive "$PIPEDRIVE_INTEGRATION_TESTS_CREDS_OAUTH" "oauth_config.json"
read_secrets source-pipedrive "$PIPEDRIVE_INTEGRATION_TESTS_CREDS_OLD" "old_config.json"
read_secrets source-quickbooks-singer "$QUICKBOOKS_TEST_CREDS"
read_secrets source-recharge "$RECHARGE_INTEGRATION_TEST_CREDS"
read_secrets source-recurly "$SOURCE_RECURLY_INTEGRATION_TEST_CREDS"
read_secrets source-redshift "$AWS_REDSHIFT_INTEGRATION_TEST_CREDS"
read_secrets source-retently "$SOURCE_RETENTLY_TEST_CREDS"
read_secrets source-s3 "$SOURCE_S3_TEST_CREDS"
read_secrets source-s3 "$SOURCE_S3_PARQUET_CREDS" "parquet_config.json"
read_secrets source-salesloft "$SOURCE_SALESLOFT_TEST_CREDS"
read_secrets source-sendgrid "$SENDGRID_INTEGRATION_TEST_CREDS"
read_secrets source-shopify "$SHOPIFY_INTEGRATION_TEST_CREDS"
read_secrets source-shopify "$SHOPIFY_INTEGRATION_TEST_OAUTH_CREDS" "config_oauth.json"
read_secrets source-shortio "$SOURCE_SHORTIO_TEST_CREDS"
read_secrets source-slack "$SOURCE_SLACK_TEST_CREDS"
read_secrets source-slack "$SOURCE_SLACK_OAUTH_TEST_CREDS" "config_oauth.json"
read_secrets source-smartsheets "$SMARTSHEETS_TEST_CREDS"
read_secrets source-snowflake "$SNOWFLAKE_INTEGRATION_TEST_CREDS" "config.json"
read_secrets source-square "$SOURCE_SQUARE_CREDS"
read_secrets source-strava "$SOURCE_STRAVA_TEST_CREDS"
read_secrets source-paystack "$SOURCE_PAYSTACK_TEST_CREDS"
read_secrets source-sentry "$SOURCE_SENTRY_TEST_CREDS"
read_secrets source-stripe "$SOURCE_STRIPE_CREDS"
read_secrets source-stripe "$STRIPE_INTEGRATION_CONNECTED_ACCOUNT_TEST_CREDS" "connected_account_config.json"
read_secrets source-surveymonkey "$SURVEYMONKEY_TEST_CREDS"
read_secrets source-tempo "$TEMPO_INTEGRATION_TEST_CREDS"
read_secrets source-tiktok-marketing "$SOURCE_TIKTOK_MARKETING_TEST_CREDS"
read_secrets source-tiktok-marketing "$SOURCE_TIKTOK_MARKETING_PROD_TEST_CREDS" "prod_config.json"
read_secrets source-trello "$TRELLO_TEST_CREDS"
read_secrets source-twilio "$TWILIO_TEST_CREDS"
read_secrets source-typeform "$SOURCE_TYPEFORM_CREDS"
read_secrets source-us-census "$SOURCE_US_CENSUS_TEST_CREDS"
read_secrets source-zendesk-chat "$ZENDESK_CHAT_INTEGRATION_TEST_CREDS"
read_secrets source-zendesk-sunshine "$ZENDESK_SUNSHINE_TEST_CREDS"
read_secrets source-zendesk-support "$ZENDESK_SUPPORT_TEST_CREDS"
read_secrets source-zendesk-support "$ZENDESK_SUPPORT_OAUTH_TEST_CREDS" "config_oauth.json"
read_secrets source-zendesk-talk "$ZENDESK_TALK_TEST_CREDS"
read_secrets source-zoom-singer "$ZOOM_INTEGRATION_TEST_CREDS"
read_secrets source-zuora "$SOURCE_ZUORA_TEST_CREDS"

write_all_secrets
exit $?

