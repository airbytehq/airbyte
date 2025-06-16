# Simplesat

This is the setup guide for the Simplesat source connector which ingests data from the simplesat API.

## Prerequisites

An API key is required for authentication and using this connector. In order to obtain an API key, you must first create a Simplesat account.

Once logged-in, you will find your API key in the account settings.You can find more about their API here https://documenter.getpostman.com/view/457268/SVfRt7WJ?version=latest

For the `answers` and `responses` endpoint, you can specify a `start_date` and `end_date` for replicating data between these dates.

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Simplesat** from the Source type dropdown.
3. Enter a name for your new source.
4. For **API Key**, enter your API key obtained in the previous step.
5. For **start_date**, enter a date in YYYY-MM-DD format (UTC timezone is assumed). Data starting from this date will be replicated.
6. For **end_date**, enter a date in YYYY-MM-DD format (UTC timezone is assumed). Data ending till this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| surveys | id | DefaultPaginator | ✅ |  ❌  |
| questions | id | DefaultPaginator | ✅ |  ❌  |
| answers | id | DefaultPaginator | ✅ |  ❌  |
| responses | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.26 | 2025-06-14 | [61304](https://github.com/airbytehq/airbyte/pull/61304) | Update dependencies |
| 0.0.25 | 2025-05-25 | [60445](https://github.com/airbytehq/airbyte/pull/60445) | Update dependencies |
| 0.0.24 | 2025-05-10 | [60148](https://github.com/airbytehq/airbyte/pull/60148) | Update dependencies |
| 0.0.23 | 2025-05-04 | [59634](https://github.com/airbytehq/airbyte/pull/59634) | Update dependencies |
| 0.0.22 | 2025-04-27 | [58965](https://github.com/airbytehq/airbyte/pull/58965) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58376](https://github.com/airbytehq/airbyte/pull/58376) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57961](https://github.com/airbytehq/airbyte/pull/57961) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57440](https://github.com/airbytehq/airbyte/pull/57440) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56809](https://github.com/airbytehq/airbyte/pull/56809) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56291](https://github.com/airbytehq/airbyte/pull/56291) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55613](https://github.com/airbytehq/airbyte/pull/55613) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55112](https://github.com/airbytehq/airbyte/pull/55112) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54493](https://github.com/airbytehq/airbyte/pull/54493) | Update dependencies |
| 0.0.13 | 2025-02-15 | [54096](https://github.com/airbytehq/airbyte/pull/54096) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53574](https://github.com/airbytehq/airbyte/pull/53574) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53069](https://github.com/airbytehq/airbyte/pull/53069) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52453](https://github.com/airbytehq/airbyte/pull/52453) | Update dependencies |
| 0.0.9 | 2025-01-18 | [52013](https://github.com/airbytehq/airbyte/pull/52013) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51430](https://github.com/airbytehq/airbyte/pull/51430) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50805](https://github.com/airbytehq/airbyte/pull/50805) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50342](https://github.com/airbytehq/airbyte/pull/50342) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49748](https://github.com/airbytehq/airbyte/pull/49748) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49427](https://github.com/airbytehq/airbyte/pull/49427) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49116](https://github.com/airbytehq/airbyte/pull/49116) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-29 | [47515](https://github.com/airbytehq/airbyte/pull/47515) | Update dependencies |
| 0.0.1 | 2024-10-01 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
