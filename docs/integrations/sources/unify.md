# Unify

<HideInUI>

This page contains the setup guide and reference information for the [Unify](https://unifygtm.com) source connector. It syncs data out of Unify using the asynchronous [Bulk API](https://docs.unifygtm.com/developers/guides/request-data/bulk-api), which is built for exporting large datasets without long-lived HTTP requests.

</HideInUI>

## Prerequisites

- A Unify account.
- A user-backed Unify API key.

## Setup guide

### Generate an API key

1. Log in to Unify and open [Settings → Developers → API keys](https://app.unifygtm.com/dashboard/settings/integrations/api-keys).
2. Create a new API key and copy it. The key is sent as the `X-Api-Key` header on every request.

### Set up the Unify connector in Airbyte

1. Enter a **Name** for the Unify source connector.
2. Enter your **API Key**.
3. (Optional) Override the **API Base URL** (defaults to `https://api.unifygtm.com`).
4. (Optional) Enter a **Start Date** as a UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`). Only records changed at or after this timestamp are synced on the first run. Defaults to the beginning of time (a full backfill).
5. (Optional) Adjust **Result Page Size**, **Poll Timeout (minutes)**, and **Concurrent Streams**. See [Performance considerations](#performance-considerations).
6. Click **Set up source** and wait for the connection test to complete.

## How it works

The Bulk API is asynchronous. For each Bulk stream, the connector:

1. **Creates a query job** (`POST {resource}/query-jobs`), scoped to records changed since the last sync.
2. **Polls the job** (`GET {resource}/query-jobs/{job_id}`) until its status is `FINISHED`.
3. **Pages through results** (`GET {resource}/query-jobs/{job_id}/results`) and emits each row.
4. **Tracks a cursor** so the next sync only requests new or changed data.

The connection check uses the synchronous `object_definitions` stream — a single `GET /data/v1/objects` — so it validates your API key without creating a Bulk job.

## Supported sync modes

The Unify source connector supports the following sync modes:

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |

The six Bulk streams support both full refresh and incremental syncs. `object_definitions` is full refresh only.

## Supported streams

| Stream                     | Bulk resource                    | Sync mode   | Cursor field | Primary key |
| :------------------------- | :------------------------------- | :---------- | :----------- | :---------- |
| `company`                  | `/data/v1/objects/company`       | Incremental | `updated_at` | `id`        |
| `person`                   | `/data/v1/objects/person`        | Incremental | `updated_at` | `id`        |
| `opportunity`              | `/data/v1/objects/opportunity`   | Incremental | `updated_at` | `id`        |
| `event`                    | `/data/v1/events`                | Incremental | `timestamp`  | `id`        |
| `sequence_enrollment`      | `/sequences/v1/enrollments`      | Incremental | `updated_at` | `id`        |
| `sequence_enrollment_step` | `/sequences/v1/enrollment-steps` | Incremental | `updated_at` | `id`        |
| `object_definitions`       | `/data/v1/objects`               | Full refresh | —           | `api_name`  |

Known columns are typed in each stream's schema, and `additionalProperties` lets any other attribute the Bulk API returns flow through (nested objects and lists arrive as JSON).

`object_definitions` is a small, synchronous full-refresh stream that lists the objects available to your API key. It backs the connection `check` and also appears in the catalog. (`user` is a standard object but is left out — it's an internal reference target for `record_owner`, not a primary export stream.)

## Performance considerations

- **Job creation is rate-limited** (~100 jobs/day). One job is created per stream per sync; incremental cursors keep each job focused.
- **Retries:** `429` and `5xx` responses are retried (up to 5 times). On `429`, the connector waits for the duration in the API's `Retry-After` header rather than using exponential backoff.
- **Concurrency:** the **Concurrent Streams** setting (`num_workers`, default `2`, max `6`) controls how many streams sync in parallel. Each parallel stream creates another Bulk job, so keep it modest to stay under the job-creation rate limit. At most one Bulk job per stream is in flight at a time.
- **Job expiry:** jobs and their results expire 24h after creation; each sync downloads results immediately after the job finishes.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Reference

This connector uses the [Unify Bulk API](https://docs.unifygtm.com/developers/guides/request-data/bulk-api). All API requests use the `https://api.unifygtm.com` endpoint by default.

For programmatic configuration, use these parameter names:

| Field                  | Required | Default                    | Description                                               |
| :--------------------- | :------: | :------------------------- | :-------------------------------------------------------- |
| `api_key`              | Yes      | —                          | User-backed Unify API key, sent as the `X-Api-Key` header. |
| `base_url`             | No       | `https://api.unifygtm.com` | API base URL.                                             |
| `start_date`           | No       | `1970-01-01T00:00:00Z`     | Only sync records changed at or after this UTC timestamp. |
| `page_size`            | No       | `1000`                     | JSON result page size (max `2000`).                       |
| `poll_timeout_minutes` | No       | `60`                       | Max minutes to wait for a single query job to finish.     |
| `num_workers`          | No       | `2`                        | Streams to sync in parallel (1–6).                        |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                       |
| :------ | :--------- | :----------- | :-------------------------------------------- |
| 0.1.0   | 2026-06-25 |              | 🎉 New Source: Unify                          |

</details>
