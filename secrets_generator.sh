#!/bin/bash
ENVFILE="$HOME/.octavia"
declare -a passwords=("airbyte/password/qogita_db" "airbyte/password/snowflake" "airbyte/password/revenue_db")

# Ensure your EC2 instance has eth most recent version of the AWS CLI
brew install jq
pip3 install awscli --upgrade

# Export the secret to .env
echo passwords;

for i in "${!passwords[@]}"
do
  aws secretsmanager get-secret-value --secret-id ${passwords[$i]} --region $AWS_REGION | \
    jq -r '.SecretString' | \
    jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]" >> $ENVFILE;
done
