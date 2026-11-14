# Linkly

<HideInUI>

This page contains the setup guide and reference information for the [Linkly](https://linklyhq.com) source connector.

</HideInUI>

[Linkly](https://linklyhq.com) is a URL shortener and click tracker. This connector uses the [Linkly REST API](https://linklyhq.com/support/api) to replicate your workspaces, short links, branded domains, daily click counts and conversions into your destination.

## Prerequisites

- A Linkly account (any plan, including Free).
- A Linkly API key. In the Linkly app, go to **Settings** > **Account Settings** > **API Access**. The key gives access to every workspace the account can see.
- A start date (`YYYY-MM-DD`). The `clicks` stream replicates the daily click time series, and the `conversions` stream the conversions Linkly recorded, from this date onwards.

## Setup guide

## Set up Linkly

1. Sign in at [app.linklyhq.com](https://app.linklyhq.com).
2. Click **Settings**, then **Account Settings**.
3. Copy the key shown in the **API Access** section.

## Set up the Linkly connector in Airbyte

<!-- env:cloud -->

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Linkly from the Source type dropdown.
4. Enter a name for the Linkly connector.
5. Enter your **API Key**.
6. Enter the **Start date** (`YYYY-MM-DD`) from which to replicate daily click counts and conversions.
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Linkly from the Source type dropdown.
4. Enter a name for the Linkly connector.
5. Enter your **API Key**.
6. Enter the **Start date** (`YYYY-MM-DD`) from which to replicate daily click counts and conversions.
7. Click **Set up source**.

<!-- /env:oss -->

### Configuration reference

| Input        | Type     | Required | Description                                                                                                                     |
| ------------ | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `api_key`    | `string` | Yes      | Your Linkly API key, sent as a Bearer token.                                                                                    |
| `start_date` | `string` | Yes      | UTC date (`YYYY-MM-DD`) from which to replicate the `clicks` time series and `conversions`. Other streams are not date-bounded. |

## Supported sync modes

The Linkly source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature           | Supported?                               |
| :---------------- | :--------------------------------------- |
| Full Refresh Sync | Yes                                      |
| Incremental Sync  | Yes (`clicks` and `conversions` streams) |
| Namespaces        | No                                       |

## Supported Streams

| Stream        | Primary key            | Pagination                            | Full refresh | Incremental                | Notes                                                                                                                      |
| ------------- | ---------------------- | ------------------------------------- | ------------ | -------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `workspaces`  | `id`                   | None                                  | Yes          | No                         | Every workspace the API key can access. Parent of the workspace-scoped streams below.                                      |
| `links`       | `id`                   | Page-based (`page`, `page_size=1000`) | Yes          | No                         | One record per short link, including destination URL, slug, UTM parameters and lifetime / 30-day / today click aggregates. |
| `domains`     | `workspace_id`, `name` | None                                  | Yes          | No                         | Custom (branded) domains configured in each workspace. `workspace_id` is added by the connector.                           |
| `clicks`      | `workspace_id`, `t`    | None                                  | Yes          | Yes (cursor `t`)           | Daily click counts per workspace from `start_date`, including bot traffic. `workspace_id` is added by the connector.       |
| `conversions` | `id`                   | Cursor (`after`, `limit=1000`)        | Yes          | Yes (cursor `inserted_at`) | Every conversion recorded in each workspace since `start_date`, oldest first. `workspace_id` is added by the connector.    |

### Incremental sync for `clicks`

The `clicks` stream uses the `t` (day) field as its cursor and requests `start`/`end` date ranges from the API. Because the current day keeps accumulating clicks after it has been synced, every incremental run re-reads the last two days (a two-day lookback window). Use a deduplicating destination sync mode (for example _Incremental | Append + Deduped_) so the earlier partial row is overwritten by the final count.

### Incremental sync for `conversions`

The `conversions` stream uses `inserted_at`, the time Linkly recorded the conversion, as its cursor and requests pages of up to 1,000 with `since` and `after`. A conversion reported late (for example, a sale a billing webhook delivers days after it happened) is recorded when it arrives, so it is picked up by the next sync even though its `occurred_at` is older. Each incremental run re-reads the hour before the saved cursor; use a deduplicating destination sync mode so those rows are overwritten rather than duplicated.

## Limitations & Troubleshooting

- **Click totals include bots.** The `clicks.y` and `links.clicks_*` figures count all traffic. The `links.human_clicks_*` fields exclude clicks with a bot signal.
- **Rate limits.** Linkly returns HTTP 429 when a key exceeds its rate limit. The connector retries with exponential backoff.
- **Invalid API key.** HTTP 401 responses are surfaced as a configuration error. Regenerating the key in Linkly invalidates the previous one.
- **Not covered yet.** Per-dimension click breakdowns (`/clicks/counters/{country|referer|...}`), hourly click frequency and the `deleted=true` (trashed) links filter are not exposed as streams.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                           |
| ------- | ---------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2026-09-13 | [85922](https://github.com/airbytehq/airbyte/pull/85922) | Initial release: `workspaces`, `links`, `domains`, `clicks` (incremental) and `conversions` (incremental) streams |

</details>
