#!/usr/bin/env bash

set -e

echo "Writing cloud storage credentials.."
export AWS_ACCESS_KEY_ID="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_access_key_id)"
export AWS_SECRET_ACCESS_KEY="$(echo "$AWS_S3_INTEGRATION_TEST_CREDS" | jq -r .aws_secret_access_key)"
export S3_LOG_BUCKET=airbyte-kube-integration-logging-test
export S3_LOG_BUCKET_REGION=us-west-2

echo "Running logging tests.."
./gradlew --no-daemon :airbyte-config:models:integrationTest  --scan
