# Cursor

This connector syncs team member, usage, and spend data from the [Cursor Admin API](https://cursor.com/docs/account/teams/admin-api) for a Cursor team.

## Prerequisites

- A Cursor team with access to the Admin API. Cursor lists the Admin API as available to Enterprise teams.
- A Cursor team administrator account, which you need to create an Admin API key.

## Setup guide

### Step 1: Create a Cursor Admin API key

1. Sign in to the [Cursor dashboard](https://cursor.com/dashboard) as a team administrator.
2. Go to **API Keys**.
3. Click **New API Key** and give the key a descriptive name.
4. Copy the key. Cursor shows the key only once. Admin API keys start with `crsr_`.

The connector authenticates with HTTP Basic authentication, using the API key as the username and an empty password. For more information, see [Cursor's API authentication documentation](https://cursor.com/docs/api#authentication).

### Step 2: Set up the connector in Airbyte

1. Create a new Cursor source.
2. In **API Key**, paste the Admin API key from Step 1.
3. In **Start Date**, enter the UTC date, in `YYYY-MM-DD` format, from which to sync the `daily_usage` and `usage_events` streams. The `members` and `spend` streams ignore this setting.
4. Click **Set up source**.

## Supported sync modes

| Stream | Full Refresh | Incremental | Cursor field |
| :--- | :---: | :---: | :--- |
| `members` | Yes | No | |
| `daily_usage` | Yes | Yes | `date` |
| `spend` | Yes | No | |
| `usage_events` | Yes | Yes | `timestamp` |

## Supported streams

| Stream | Cursor endpoint | Primary key | Description |
| :--- | :--- | :--- | :--- |
| `members` | [`GET /teams/members`](https://cursor.com/docs/account/teams/admin-api#get-team-members) | `email` | All members of the team, including their role and whether they were removed from the team. |
| `daily_usage` | [`POST /teams/daily-usage-data`](https://cursor.com/docs/account/teams/admin-api#get-daily-usage-data) | `date`, `email` | One record per team member per day, with metrics such as lines added and deleted, accepted suggestions, Tab completions, and Chat, Agent, and Composer request counts. |
| `spend` | [`POST /teams/spend`](https://cursor.com/docs/account/teams/admin-api#get-spending-data) | `email` | Spend per team member for the current billing cycle, including on-demand and total spend in cents and per-user spend limits. |
| `usage_events` | [`POST /teams/filtered-usage-events`](https://cursor.com/docs/account/teams/admin-api#get-usage-events-data) | `timestamp`, `userEmail`, `model` | Individual usage events with the model, billing category, token usage, and charged cost in cents. |

### Stream details

- **`daily_usage`**: The connector requests this endpoint with pagination, so the API returns a record for every team member who had a membership during the requested date range, not only active members. The `isActive` field shows whether the member had activity that day. The `subscriptionIncludedReqs`, `usageBasedReqs`, and `apiKeyReqs` fields count raw usage events, not billable request units. To calculate billable requests, sum `requestsCosts` in the `usage_events` stream.
- **`spend`**: The API returns spend for the current billing cycle only. Each sync replaces the previous values. To keep a history of spend over time, use the **Full Refresh | Append** sync mode, which stores a new copy of every record on each sync.
- **`usage_events`**: To reconcile event-level costs with the totals in the `spend` stream, sum the `chargedCents` field.

### Incremental syncs

The `daily_usage` and `usage_events` streams request data in 30-day windows, because the Cursor API doesn't accept date ranges longer than 30 days. Cursor aggregates usage data hourly, so recent values can change after the connector reads them. To pick up those changes, the connector re-reads the last 2 days of `daily_usage` data and the last day of `usage_events` data on every incremental sync. Use the **Incremental | Append + Deduped** sync mode for these streams to avoid duplicate records in your destination.

## Limitations

The Cursor Admin API limits most endpoints, including `/teams/members`, `/teams/daily-usage-data`, and `/teams/spend`, to 20 requests per minute per team. The `/teams/filtered-usage-events` endpoint allows 60 requests per minute. When the API returns a `429` or `5xx` response, the connector waits for the time in the `Retry-After` header, or increases the wait time exponentially, and retries up to 5 times. For more information, see [Cursor's rate limit documentation](https://cursor.com/docs/api#rate-limits).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-07 | [82708](https://github.com/airbytehq/airbyte/pull/82708) | Initial release by [@dhlotter](https://github.com/dhlotter) via Connector Builder |

</details>
