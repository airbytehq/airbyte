---
products: embedded
---

# Prerequisites and setup

Before you can start using Embedded, complete the following one-time setup process.

## Prerequisites

1. Receive the following values from your Airbyte account representative. If you don't have one, [please reach out to our team](https://airbyte.com/company/talk-to-sales). Then, create an `.env` file with the following:

    ```yaml
    AIRBYTE_ORGANIZATION_ID=
    AIRBYTE_CLIENT_ID=
    AIRBYTE_CLIENT_SECRET=
    EXTERNAL_USER_ID=
    ```

    The `EXTERNAL_USER_ID` is a unique identifier you create and assign when generating an Embedded Widget. It's the identifier used to differentiate between unique users. You should create one unique identifier for each of your users. For testing, you may set `EXTERNAL_USER_ID=0`.

2. Configure or prepare an S3 bucket to load customer data to. Obtain the following values required to read from and write to the bucket to be used later during setup:

    ```yaml
    AWS_S3_ACCESS_KEY_ID=
    AWS_S3_SECRET_ACCESS_KEY=
    S3_BUCKET_NAME=
    S3_PATH_PREFIX=
    S3_BUCKET_REGION=
    ```

## One-time setup

Before submitting requests to Airbyte, you’ll need to use your Client ID and Client Secret to generate the access key used for API request authentication. You can use the following [cURL to create an access key](https://reference.airbyte.com/reference/createaccesstoken#/):

```sh
curl --request POST \
     --url https://api.airbyte.com/v1/applications/token \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
      {
        "client_id": "<client_id>",
        "client_secret": "<client_secret>",
        "grant-type": "<client_credentials>"
      }'
```

Next, you’ll need to create a connection template. You only need to do this once. The template describes where your customer data will land, and at what frequency to sync customer data. By default, syncs will run every hour. Here’s an example cURL API request for creating an S3 destination using the values obtained earlier to connect to an S3 bucket:

```sh
curl --location --request POST 'https://api.airbyte.com/v1/config_templates/connections' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data '{
    "destinationName": "destination-s3", 
    "organizationId": "<ORGANIZATION_ID>",
    "destinationActorDefinitionId": "4816b78f-1489-44c1-9060-4b19d5fa9362",
      "destinationConfiguration": {
        "access_key_id": "<AWS_S3_ACCESS_KEY_ID>",
        "secret_access_key": "<AWS_S3_SECRET_ACCESS_KEY>",
        "s3_bucket_name": "<S3_BUCKET_NAME>",
        "s3_bucket_path": "<S3_PATH_PREFIX>",
        "s3_bucket_region": "<S3_BUCKET_REGION>",
        "format": {
          "format_type": "CSV",
          "flattening": "Root level flattening"
          }
        }
      }
    }'
```

Once this succeeds, you are ready to send customer data through Airbyte.

## Install node.js and npm

Before you can complete the tutorial on the next page, you must [install Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
