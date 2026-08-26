# Dust

[Dust](https://dust.tt) is an AI platform for building and running custom agents on top of a company's tools and data. This source syncs workspace analytics from Dust: message and conversation volume, active users, agent and tool usage, and message-level metadata.

Every stream reads from the same Dust endpoint, [Export workspace analytics](https://docs.dust.tt/docs/workspace-analytics#accessing-analytics-via-the-api) (`GET https://dust.tt/api/v1/w/{workspace_id}/analytics/export`), requesting one analytics `table` per stream.

## Prerequisites

- A Dust workspace hosted at `dust.tt`. Workspaces in Dust's European region (`eu.dust.tt`) aren't supported, because the connector always calls `dust.tt`.
- A Dust API key with workspace admin scope. Dust returns `403` for the analytics export endpoint if the key isn't an admin key.
- Your Dust workspace ID.

## Setup guide

### Step 1: Create a Dust API key

You must be an admin of the Dust workspace to create the key.

1. In Dust, go to **Admin** > **API & Programmatic** > **API Keys**.
2. Click **Create an API Key** and name it.
3. Copy the key and store it somewhere safe. Dust hides the value shortly after creation and you can't retrieve it again.

### Step 2: Find your workspace ID

Open your workspace in Dust and copy the identifier that follows `dust.tt/w/` in the URL. In `https://dust.tt/w/a1b2c3d4e5/spaces`, the workspace ID is `a1b2c3d4e5`.

### Step 3: Configure the source in Airbyte

1. Paste the API key into **Bearer Token** and the workspace identifier into **Workspace ID**.
2. Set **Start Date** to the first day you want to sync, in `YYYY-MM-DD` format. This field is required.
3. Optionally set **End Date** in `YYYY-MM-DD` format to stop syncing at a fixed day. If you leave it empty, the connector syncs through the previous UTC day, so data for the current day never appears in a sync.

## Supported streams

| Stream | Dust analytics table | Contents |
| -------- | ---------------------- | ---------- |
| `usage_metrics` | `usage_metrics` | Daily messages, conversations, and active users. |
| `active_users` | `active_users` | Daily, weekly, and monthly active user counts. |
| `source` | `source` | Message volume by origin, such as the web app, Slack, or the API. |
| `tool_usage` | `tool_usage` | Tool executions and unique users per day. |
| `skill_usage` | `skill_usage` | Skill executions and unique users per day. |
| `agents` | `agents` | Top agents by message count. |
| `users` | `users` | Top users by message count. |
| `messages` | `messages` | Message-level log. Dust exports metadata only and never message content. |

Dust also exposes `skills` and `feedback` analytics tables, which this connector doesn't sync.

### Sync behavior

All streams except `agents` sync incrementally on a date cursor: `date` for the daily aggregate streams, `createdAt` for `messages`, and `snapshot_date` for `users`. These streams request one day of data at a time, so a backfill that starts years in the past issues one request per day per stream and the first sync of a long history takes a while.

Dust doesn't return `snapshot_date` for the `users` table. The connector adds it from the day being requested, which makes `users` a daily snapshot of that day's top users rather than a single ranked list.

The `agents` stream is full refresh only. Each sync re-requests the whole configured date range and returns the top agents for that window.

Because `agents` and `users` are ranked tables, they cover the most active agents and users for the requested window rather than every agent or member of the workspace.

## Troubleshooting

- **403 responses**: the API key doesn't have admin scope. Create a new key as a workspace admin.
- **Slow authentication failures**: the connector retries `401` responses three times, waiting 30 seconds between attempts, so an invalid or revoked token takes about a minute and a half to surface as an error.
- **Rate limiting and server errors**: the connector retries `429`, `500`, `502`, `503`, and `504` responses up to five times with exponential backoff. Dust doesn't publish a documented rate limit for the analytics export endpoint.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_date` | `string` | End Date. The end date for the extracted data in YYYY-MM-DD format |  |
| `start_date` | `string` | Start Date. The start date for data extraction in YYYY-MM-DD format |  |
| `bearer_token` | `string` | Bearer Token. Token needed for authentication to dust |  |
| `workspace_id` | `string` | Workspace ID. Unique string identifier for the workspace |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| usage_metrics | date | No pagination | ✅ |  ✅  |
| active_users | date | No pagination | ✅ |  ✅  |
| source | date.source | No pagination | ✅ |  ✅  |
| tool_usage | date.toolName | No pagination | ✅ |  ✅  |
| skill_usage | date.skillName | No pagination | ✅ |  ✅  |
| agents | agentId | No pagination | ✅ |  ❌  |
| users | userId.snapshot_date | No pagination | ✅ |  ✅  |
| messages | messageId | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2026-08-26 | [85031](https://github.com/airbytehq/airbyte/pull/85031) | Enable acceptance tests |
| 0.0.5 | 2026-08-18 | [84577](https://github.com/airbytehq/airbyte/pull/84577) | Update dependencies |
| 0.0.4 | 2026-08-11 | [83911](https://github.com/airbytehq/airbyte/pull/83911) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83458](https://github.com/airbytehq/airbyte/pull/83458) | Update dependencies |
| 0.0.2 | 2026-07-28 | [82897](https://github.com/airbytehq/airbyte/pull/82897) | Update dependencies |
| 0.0.1 | 2026-07-27 | [81402](https://github.com/airbytehq/airbyte/pull/81402) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
