# Bored-API

This page contains the setup guide and reference information for the [Bored-API](https://www.boredapi.com/documentation) source connector.

## Prerequisites

Api key is not mandate for this connector to work, But a dummy API need to be passed for establishing the connection. Example: 12345
Just pass the dummy API key and optional parameters for establishing the connection.

## Setup guide

### Step 1: Set up Bored-API connection

- Get a dummy API key (Example: 12345)
- Params (If specific info is needed)
- Available params
  - "key" Example: "5881028",
  - "type" Example: "recreational",
  - "participants" Example: "1",
  - "price" Example: "0.0",
  - "minprice" Exmaple: "0",
  - "maxprice" Example: "0.1",
  - "accessibility" Example: "1",
  - "minaccessibility" Example: "0",
  - "maxaccessibility" Example: "0.1"

## Step 2: Set up the Bored-API connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Bored-API connector and select **Bored-API** from the Source type dropdown.
4. Enter your dummy `api_key`.
5. Enter the params configuration if needed. Supported params: key, type, participants, price, accessibility
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your dummy `api_key`.
5. Enter the params configuration if needed. Supported params: key, type, participants, price, accessibility
6. Click **Set up source**.

## Supported sync modes

The Bored-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- activity_with_key

## API method example

GET http://www.boredapi.com/api/activity?key=5881028

## Performance considerations

Bored-API's [API reference](https://www.boredapi.com/documentation) has v1 at development. The connector as default uses v1.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-11-01 | [Init](https://github.com/airbytehq/airbyte/pull/<yet>)| Initial commit |