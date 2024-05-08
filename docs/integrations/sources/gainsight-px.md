# Gainsight-API

This page contains the setup guide and reference information for the [Gainsight-PX-API](https://gainsightpx.docs.apiary.io/) source connector from [Gainsight-PX](https://support.gainsight.com/PX/API_for_Developers)

## Prerequisites

Api key is mandate for this connector to work, It could be generated from the dashboard settings (ref - https://app.aptrinsic.com/settings/api-keys).

## Setup guide

### Step 1: Set up Gainsight-API connection

- Generate an API key (Example: 12345)
- Params (If specific info is needed)
- Available params
  - api_key: The aptrinsic api_key

## Step 2: Set up the Gainsight-APIs connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Gainsight-API connector and select **Gainsight-API** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter the params configuration if needed. Supported params are: query, orientation, size, color, locale, collection_id \
   video_id, photo_id
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter the params configuration if needed. Supported params are: query, orientation, size, color, locale, collection_id \
   video_id, photo_id
5. Click **Set up source**.

## Supported sync modes

The Gainsight-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- accounts
- admin_attributes
- articles
- feature
- kcbot
- segments
- user_attributes
- users

## API method example

GET https://api.aptrinsic.com/v1/accounts

## Performance considerations

Gainsight-PX-API's [API reference](https://gainsightpx.docs.apiary.io/) has v1 at present. The connector as default uses v1.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                 |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------- |
| 0.1.1   | 2024-05-03 | [37593](https://github.com/airbytehq/airbyte/pull/37593) | Changed `last_records` to `last_record` |
| 0.1.0   | 2023-05-10 | [26998](https://github.com/airbytehq/airbyte/pull/26998) | Initial PR                              |
