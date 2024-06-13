# DataScope

This page contains the setup guide and reference information for the [DataScope](https://dscope.github.io/docs/) source connector.

## Prerequisites

A DataScope account with access to the API. You can create a free account [here](https://www.mydatascope.com/webhooks).

## Setup guide

### Step 1: Set up DataScope connection

- Create a DataScope account
- Create an API key and copy it to Airbyte

## Step 2: Set up the DataScope connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the DataScope connector and select **DataScope** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter the params configuration if needed. Supported params are: sort, alt, prettyPrint (Optional)
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key` which will be flagged with Authorization header.
4. Click **Set up source**.

## Supported sync modes

The DataScope source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Locations
- answers

Implemented but not added streams:

- Lists
- Notifications

## API method example

GET https://www.mydatascope.com/api/external/locations

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject        |
| :------ | :--------- | :-------------------------------------------------------- | :------------- |
| 0.1.3   | 2024-06-15 | [38844](https://github.com/airbytehq/airbyte/pull/38844)  | Make compatible with builder |
| 0.1.2   | 2024-06-06 | [39254](https://github.com/airbytehq/airbyte/pull/39254)  | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1   | 2024-05-20 | [38440](https://github.com/airbytehq/airbyte/pull/38440)  | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-31 | [#18725](https://github.com/airbytehq/airbyte/pull/18725) | Initial commit |

</details>
