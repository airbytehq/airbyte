# Punk-API

This page contains the setup guide and reference information for the [Punk-API](https://punkapi.com/documentation/v2) source connector.

## Prerequisites

Api key is not required for this connector to work,But a dummy key need to be passed to enhance in next versions. Example:123

## Setup guide

### Step 1: Set up Punk-API connection

- Pass a dummy API key (Example: 12345)
- Params (Optional ID)

## Step 2: Set up the Punk-API connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Punk-API connector and select **Punk-API** from the Source type dropdown.
4. Enter your dummy `api_key`.
5. Enter the params configuration if needed: ID (Optional)
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your dummy `api_key`.
4. Enter the params configuration if needed: ID (Optional)
5. Click **Set up source**.

## Supported sync modes

The Punk-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Beers
- Beers_with_ID

## API method example

GET https://api.punkapi.com/v2/beers

## Performance considerations

Punk API's [API reference](https://punkapi.com/documentation/v2) has v2 at present and v1 as depricated. The connector as default uses v2.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                            | Subject        |
| :------ | :--------- | :------------------------------------------------------ | :------------- |
| 0.1.2 | 2024-06-06 | [39158](https://github.com/airbytehq/airbyte/pull/39158) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38441](https://github.com/airbytehq/airbyte/pull/38441) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-31 | [Init](https://github.com/airbytehq/airbyte/pull/<yet>) | Initial commit |

</details>
