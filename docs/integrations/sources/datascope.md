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
| 0.2.13 | 2025-02-08 | [53323](https://github.com/airbytehq/airbyte/pull/53323) | Update dependencies |
| 0.2.12 | 2025-02-01 | [52809](https://github.com/airbytehq/airbyte/pull/52809) | Update dependencies |
| 0.2.11 | 2025-01-25 | [52302](https://github.com/airbytehq/airbyte/pull/52302) | Update dependencies |
| 0.2.10 | 2025-01-18 | [51649](https://github.com/airbytehq/airbyte/pull/51649) | Update dependencies |
| 0.2.9 | 2025-01-11 | [51069](https://github.com/airbytehq/airbyte/pull/51069) | Update dependencies |
| 0.2.8 | 2024-12-28 | [50569](https://github.com/airbytehq/airbyte/pull/50569) | Update dependencies |
| 0.2.7 | 2024-12-21 | [49542](https://github.com/airbytehq/airbyte/pull/49542) | Update dependencies |
| 0.2.6 | 2024-12-12 | [49161](https://github.com/airbytehq/airbyte/pull/49161) | Update dependencies |
| 0.2.5 | 2024-11-05 | [48357](https://github.com/airbytehq/airbyte/pull/48357) | Revert to source-declarative-manifest v5.17.0 |
| 0.2.4 | 2024-11-05 | [48336](https://github.com/airbytehq/airbyte/pull/48336) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47857](https://github.com/airbytehq/airbyte/pull/47857) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47451](https://github.com/airbytehq/airbyte/pull/47451) | Update dependencies |
| 0.2.1 | 2024-10-21 | [47206](https://github.com/airbytehq/airbyte/pull/47206) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44416](https://github.com/airbytehq/airbyte/pull/44416) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-17 | [44213](https://github.com/airbytehq/airbyte/pull/44213) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43764](https://github.com/airbytehq/airbyte/pull/43764) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43063](https://github.com/airbytehq/airbyte/pull/43063) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42832](https://github.com/airbytehq/airbyte/pull/42832) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42269](https://github.com/airbytehq/airbyte/pull/42269) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41837](https://github.com/airbytehq/airbyte/pull/41837) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41373](https://github.com/airbytehq/airbyte/pull/41373) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41304](https://github.com/airbytehq/airbyte/pull/41304) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40815](https://github.com/airbytehq/airbyte/pull/40815) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40302](https://github.com/airbytehq/airbyte/pull/40302) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40193](https://github.com/airbytehq/airbyte/pull/40193) | Update dependencies |
| 0.1.3 | 2024-06-15 | [38844](https://github.com/airbytehq/airbyte/pull/38844) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39254](https://github.com/airbytehq/airbyte/pull/39254) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38440](https://github.com/airbytehq/airbyte/pull/38440) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-31 | [#18725](https://github.com/airbytehq/airbyte/pull/18725) | Initial commit |

</details>
