#!/usr/bin/bash

mkdir ~/.aws

# cat <<EOF >> ~/.aws/credentials
# [default]
# aws_access_key_id = $1
# aws_secret_access_key = $2
# EOF

cat <<EOF >> ~/.aws/config
[default]
region=us-east-2
EOF