# Wikipedia Pageviews

This page contains the setup guide and reference information for the [Wikipedia Pageviews](https://wikimedia.org/api/rest_v1/#/Pageviews%20data) source connector.

## Prerequisites

None

## Setup guide

## Step 1: Set up the Courier connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Courier connector and select **Wikipedia Pageviews** from the Source type dropdown.
4. Enter your parameters.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your parameters.
4. Click **Set up source**.

## Supported sync modes

The Wikipedia Pageviews source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- per-article
- top

## Performance considerations

100 req/s per endpoint.

## Changelog

| Version | Date       | Pull Request                                              | Subject        |
| :------ | :--------- | :-------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-31 | [#18343](https://github.com/airbytehq/airbyte/pull/18343) | Initial commit |
