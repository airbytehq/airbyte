#!/usr/bin/env bash

set -e

echo "Writing cloud storage credentials.."

# S3
export AWS_ACCESS_KEY_ID="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_access_key_id)"
export AWS_SECRET_ACCESS_KEY="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_secret_access_key)"
export S3_LOG_BUCKET=airbyte-kube-integration-logging-test
export S3_LOG_BUCKET_REGION=us-west-2

# GCS
echo "$GOOGLE_CLOUD_STORAGE_TEST_CREDS" > "/tmp/gcs.json"
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gcs.json"
export GCP_STORAGE_BUCKET=airbyte-kube-integration-logging-test

echo "Running logging tests.."
SUB_BUILD=PLATFORM ./gradlew --no-daemon :airbyte-config:models:integrationTest  --scan
