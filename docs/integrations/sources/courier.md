# Courier

This page contains the setup guide and reference information for the [Courier](https://www.courier.com/) source connector.

## Prerequisites

Generate an API key per the [Courier documentation](https://www.courier.com/docs/guides/getting-started/go/#getting-your-api-keys).

## Setup guide

### Step 1: Set up Courier

- Courier Account
- Courier API Key

## Step 2: Set up the Courier connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Courier connector and select **Courier** from the Source type dropdown.
4. Enter your `api_key`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Click **Set up source**.

## Supported sync modes

The Courier source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Messages

## Performance considerations

Courier's [API reference](https://www.courier.com/docs/reference/) does not address rate limiting but the connector implements exponential backoff when a 429 response status code is received.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-09-10 | [TODO](https://github.com/airbytehq/airbyte/pull/TODO) | Initial commit |
