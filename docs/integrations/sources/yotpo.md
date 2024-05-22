# Yotpo

This page contains the setup guide and reference information for the [Yotpo](https://apidocs.yotpo.com/reference/welcome) source

## Prerequisites

Access Token (which acts as bearer token) is mandate for this connector to work, It could be generated from the auth token call (ref - https://apidocs.yotpo.com/reference/yotpo-authentication).

## Setup guide

### Step 1: Set up Yotpo connection

- Generate an Yotpo access token via auth endpoint (ref - https://apidocs.yotpo.com/reference/yotpo-authentication)
- Setup params (All params are required)
- Available params
  - access_token: The generated access token
  - app_key: Seen at the yotpo settings (ref - https://settings.yotpo.com/#/general_settings)
  - start_date: Date filter for eligible streams, enter
  - email: Registered email address

## Step 2: Set up the Yotpo connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Yotpo connector and select **Yotpo** from the Source type dropdown.
4. Enter your `access_token, app_key, start_date and email`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `access_token, app_key, start_date and email`.
4. Click **Set up source**.

## Supported sync modes

The Yotpo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- email_analytics
- raw_data
- reviews
- unsubscribers
- webhooks
- webhook_events

## API method example

GET https://api.yotpo.com/v1/apps/APPAAAAAATTTTTTDDDDDD/reviews?utoken=abcdefghikjlimls

## Performance considerations

Yotpo [API reference](https://api.yotpo.com/v1/) has v1 at present. The connector as default uses v1 and changed according to different endpoints.

## Changelog

| Version | Date       | Pull Request                                            | Subject        |
| :------ | :--------- | :------------------------------------------------------ | :------------- |
| 0.1.0   | 2023-04-14 | [Init](https://github.com/airbytehq/airbyte/pull/25532) | Initial commit |
