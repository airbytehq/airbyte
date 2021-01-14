#!/usr/bin/env bash

set -e

# This script should only be used to set up the status site for the first time or to make your own version for testing.
# Prod refers to the prod environment used for prior Airbyte projects.

BUCKET=airbyte-status
PROFILE=prod
REGION=us-east-2

echo "Creating bucket..."
aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"  --create-bucket-configuration LocationConstraint="$REGION" --profile "$PROFILE"

echo "Setting policy for bucket..."
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file://"$(pwd)"/tools/status/policy.json --profile "$PROFILE"

echo "Uploading default files..."
aws s3 sync "$(pwd)"/tools/status/defaults/ s3://"$BUCKET"/ --profile "$PROFILE"

echo "Setting bucket as website..."
aws s3 website s3://"$BUCKET"/ --index-document index.html --error-document error.html --profile "$PROFILE"

echo "Site should be ready at http://$BUCKET.s3-website.$REGION.amazonaws.com"
