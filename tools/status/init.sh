#!/usr/bin/env bash

set -e

# This script should only be used to set up the status site for the first time or to make your own version for testing.
# TODO move this setup to terraform

BUCKET=airbyte-connector-build-status
PROFILE=dev # AWS dev environment
REGION=us-east-2
S3_DOMAIN="$BUCKET.s3-website.$REGION.amazonaws.com"

export AWS_PAGER=""

echo "This has already been created. Comment out this line if you really want to run this again." && exit 1

echo "Creating bucket..."
aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"  --create-bucket-configuration LocationConstraint="$REGION" --profile "$PROFILE"

echo "Setting policy for bucket..."
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file://"$(pwd)"/tools/status/policy.json --profile "$PROFILE"

echo "Uploading default files..."
aws s3 sync "$(pwd)"/tools/status/defaults/ s3://"$BUCKET"/ --profile "$PROFILE"

echo "Setting bucket as website..."
aws s3 website s3://"$BUCKET"/ --index-document index.html --error-document error.html --profile "$PROFILE"


aws cloudfront create-distribution \
    --origin-domain-name $S3_DOMAIN \
    --default-root-object index.html \
    --profile "$PROFILE"

echo "Site should be ready at http://$S3_DOMAIN"
echo "1. Add a certificate and cname to the distribution: https://advancedweb.hu/how-to-use-a-custom-domain-on-cloudfront-with-cloudflare-managed-dns/"
echo "2. Configure a CNAME on Cloudflare for status-api.airbyte.io to point to the bucket!"
echo "3. Create STATUS_API_AWS_ACCESS_KEY_ID and STATUS_API_AWS_SECRET_ACCESS_KEY Github secrets with access to the bucket."
