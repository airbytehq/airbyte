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
| 0.0.1 | 2024-10-01 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
