---
products: embedded
---

# Prerequisites and setup

This guide walks you through how to configure Airbyte Embedded and run the Embedded Widget in a [sample Node.js app](https://github.com/airbytehq/embedded-sampleweb-nodejs). Before you can start using Embedded, please complete the following one-time setup process.

## Airbyte credentials

To use Airbyte Embedded, must have an active Airbyte Cloud, or OSS, instance with Embedded enabled. (Please [contact sales](https://share.hsforms.com/2uRdBz9VoTWiCtjECzRYgawcvair) if you would like to sign up for Airbyte Embedded).
Once you have you your Airbyte instance available, log in and note down the following values. You need these to configure the web app and one-time setup.

- Organization ID: Unique identifier to your Airbyte instance. Obtained via Settings > Embedded.
- Client ID: Unique API id. Obtained via Settings > Applications > Create Application.
- Client Secret: Secret key for authentication . Obtained via Settings > Applications.
- External User ID: A unique identifier you create and assign when generating an Embedded Widget. It's the identifier used to differentiate between unique users. You should create one unique identifier for each of your users. For testing, you may set it to 0.

If you are still unsure where to retrieve these values, please [watch this video](https://youtu.be/H6ik3HAj0iY) for a walkthrough.

## Create a .env file

Once you have the credentials, create a new `.env` file, based on the `.env.example` container within the [sample app repo](https://github.com/airbytehq/embedded-sampleweb-nodejs). You also need this .env file in the next step, when configuring the web app. Go ahead and set the following keys in the .env to the values you obtained in the preceding section.

```bash
AIRBYTE_ORGANIZATION_ID=your_organization_id
AIRBYTE_CLIENT_ID=your_client_id
AIRBYTE_CLIENT_SECRET=your_client_secret
```

## Configure S3 for storing users

Users created via Embedded are stored in S3 buckets managed by you. Once you have the `.env` created with Airbyte credentials, go ahead and create an [S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html) and add the following values to the `.env`:

### AWS credentials

```bash
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# S3 Configuration
S3_BUCKET=your_s3_bucket_name
S3_BUCKET_REGION=your_s3_bucket_region
S3_BUCKET_PREFIX=your_s3_bucket_prefix
```

Next, configure Airbyte to use the S3 bucket. Create a new shell script, `setup.sh` with the following code. From the command line, execute the following script to create the required connection. You can also retrieve the code from [this repo](https://github.com/airbytehq/embedded-sampleweb-nodejs/blob/main/setup.sh).

```bash
#!/bin/bash

# Enable debug mode to show commands as they execute
set -x

echo "=== Starting Airbyte Setup ==="

# Load .env file
echo "Loading environment variables from .env"
source .env

# Check if required variables are set
echo "Checking required environment variables..."
REQUIRED_VARS=("AIRBYTE_CLIENT_ID" "AIRBYTE_CLIENT_SECRET" "AIRBYTE_ORGANIZATION_ID" 
               "AWS_ACCESS_KEY" "AWS_SECRET_ACCESS_KEY" "S3_BUCKET" 
               "S3_BUCKET_REGION" "S3_BUCKET_PREFIX")

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "ERROR: Required variable $var is not set in .env file"
    exit 1
  else
    echo "✓ $var is set"
  fi
done

echo "All required variables are set"

# Get Access Token from Airbyte API
echo "Requesting access token from Airbyte API..."
TOKEN_RESPONSE=$(curl -sX POST \
  'https://api.airbyte.com/v1/applications/token' \
  -H 'Content-Type: application/json' \
  -d "{
    \"client_id\": \"${AIRBYTE_CLIENT_ID}\",
    \"client_secret\": \"${AIRBYTE_CLIENT_SECRET}\",
    \"grant-type\": \"client_credentials\"
  }")

# Check if token request was successful
if [[ $TOKEN_RESPONSE == *"access_token"* ]]; then
  ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
  echo "✓ Successfully obtained access token"
else
  echo "ERROR: Failed to get access token. Response:"
  echo "$TOKEN_RESPONSE" | jq '.'
  exit 1
fi

# Create connection template that will replicate data to S3
echo "Creating connection template for S3..."
CONN_RESPONSE=$(curl -X POST 'https://api.airbyte.com/v1/config_templates/connections' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -d "{
      \"destinationName\": \"S3-embedded\", 
      \"organizationId\": \"${AIRBYTE_ORGANIZATION_ID}\", 
      \"destinationActorDefinitionId\": \"4816b78f-1489-44c1-9060-4b19d5fa9362\",
      \"destinationConfiguration\": {
        \"access_key_id\": \"${AWS_ACCESS_KEY}\",
        \"secret_access_key\": \"${AWS_SECRET_ACCESS_KEY}\",
        \"s3_bucket_name\": \"${S3_BUCKET}\",
        \"s3_bucket_path\": \"${S3_BUCKET_PREFIX}\",
        \"s3_bucket_region\": \"${S3_BUCKET_REGION}\",
        \"format\": {
            \"format_type\": \"CSV\",
            \"compression\": {
                \"compression_type\": \"No Compression\"
            },
        \"flattening\": \"No flattening\"
      }
    }
  }
}")

# Print the full response for debugging
echo "Connection template response:"
echo "$CONN_RESPONSE" | jq '.'

# Check if connection creation was successful
if [[ $CONN_RESPONSE == *"id"* ]]; then
  CONFIG_TEMPLATE_ID=$(echo $CONN_RESPONSE | jq -r '.id')
  echo "✓ Successfully created connection template with ID: $CONFIG_TEMPLATE_ID"
  echo "✓ Setup completed successfully!"
else
  echo "ERROR: Failed to create connection template. Response:"
  echo "$CONN_RESPONSE" | jq '.'
  exit 1
fi

echo "=== Setup Complete ==="

# Disable debug mode
set +x
```

Run the script from the command line:

```bash
./setup.sh
```

Once you see confirmation that you set up the connection correctly, your Airbyte Embedded environment is ready to go.

## Install node.js and npm

Before you can complete the tutorial on the next page, you must [install Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
