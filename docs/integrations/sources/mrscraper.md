# MrScraper

<HideInUI>

This page contains the setup guide and reference information for the [MrScraper](https://mrscraper.com) source connector.

</HideInUI>

[MrScraper](https://mrscraper.com) is a web scraping and structured data extraction service. This connector syncs the results MrScraper stores for your scraper runs: AI extraction runs and reruns, bulk jobs, manual and workflow runs, and Web Unblocker page fetches.

## Prerequisites

- A MrScraper account
- A MrScraper API token, which authenticates the connector to your account

## Setup guide

### Set up MrScraper

1. Sign in to the [MrScraper dashboard](https://app.mrscraper.com).
2. Select your profile icon in the top-right corner, then select **API Tokens**, or go to [app.mrscraper.com/api-tokens](https://app.mrscraper.com/api-tokens).
3. Select **New Token**, enter a descriptive name, choose an expiration date, and select **Create**.
4. Copy the token. The connector stops working when the token expires or is deleted, so choose an expiration date that fits how long you plan to sync.

### Set up the MrScraper connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select MrScraper from the Source type dropdown.
4. Enter a name for the MrScraper connector.
5. Enter your **API Token**.
6. Optionally, enter a **Start Date** in `YYYY-MM-DD` format to skip older results.
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **MrScraper** from the Source type dropdown.
4. Enter a name for the MrScraper connector.
5. Enter your **API Token**.
6. Optionally, enter a **Start Date** in `YYYY-MM-DD` format to skip older results.
7. Click **Set up source**.

<!-- /env:oss -->

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Token. Your MrScraper API token. Create one on the API Tokens page of the MrScraper dashboard: https://app.mrscraper.com/api-tokens |  |
| `start_date` | `string` | Start Date. Earliest creation date (UTC) of the results to sync, in YYYY-MM-DD format. Leave it empty to sync every stored result. |  |

## Supported sync modes

The MrScraper source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append
- Incremental - Append + Deduped

## Supported Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| results | id | DefaultPaginator | ✅ |  ✅  |

Each `results` record is one stored result of a MrScraper run. It includes the run type, target URL, status, error, plan token usage, run time, and the stored output in `data`: extracted records for AI runs, or the page body in `data.html` for Web Unblocker and HTML runs. Incremental syncs use `createdAt` as the cursor.

## Limitations & Troubleshooting

<details>
<summary>Expand to see details about MrScraper connector limitations and troubleshooting.</summary>

### Connector limitations

#### Rate limiting

The connector retries rate-limited (HTTP 429) and server error responses with exponential backoff.

#### Incremental syncs read whole days

MrScraper filters results by the UTC calendar date of `createdAt`, so the cursor has one-day precision. Each incremental sync starts one day before the saved cursor, which picks up results that finished after the previous sync started, and re-reads results from those days. Use **Incremental - Append + Deduped** to keep one row per result. A result that changes more than a day after it was created, such as a long bulk job, is only updated by a full refresh.

#### Credentials are never synced

MrScraper stores a `curl` command with Web Unblocker, workflow, and HTML results, and that command contains the API token used for the request. The connector removes the `curl` field from every record, and the stream schema doesn't declare it.

#### Performance considerations

Web Unblocker results contain the full page HTML, so a single record can be hundreds of kilobytes and a page of 50 results can exceed 15 MB. Set a **Start Date** to limit the first sync.

### Troubleshooting

- `MrScraper rejected the API token`: the token is invalid, expired, or deleted. Create a new token on the [API Tokens](https://app.mrscraper.com/api-tokens) page and update the source.

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-05 | | Initial release |

</details>
