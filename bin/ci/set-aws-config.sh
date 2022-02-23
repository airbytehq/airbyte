#!/bin/bash

rm -rf ~/.aws || echo "folder does not exist"
mkdir ~/.aws

echo "
[ci]
aws_access_key_id=${AWS_ACCESS_KEY_ID}
aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}
region=us-east-1
output=json
" >> ~/.aws/credentials

echo "
[profile prd-data-dev-iam-PlatformAdmin]
source_profile=ci
role_arn=arn:aws:iam::580776257674:role/PlatformAdmin
[profile prd-data-stg-iam-PlatformAdmin]
source_profile=ci
role_arn=arn:aws:iam::074505835657:role/PlatformAdmin
[profile prd-data-prd-iam-PlatformAdmin]
source_profile=ci
role_arn=arn:aws:iam::375060456233:role/PlatformAdmin
[profile prd-shared-services-PlatformAdmin]
source_profile=ci
role_arn=arn:aws:iam::856154240248:role/PlatformAdmin
" >> ~/.aws/config

export AWS_SDK_LOAD_CONFIG=true
