# Reprise

[Reprise](https://www.reprise.com/) is a demo platform that sales, marketing, and pre-sales teams use to build interactive product tours (Replay) and cloned software environments (Replicate). This source syncs viewer analytics from the Reprise Data API: session activity, session summaries, aggregate metrics, and a change feed.

## Prerequisites

- A Reprise subscription that includes Data API access.
- An API token created in the Reprise portal under **Settings** > **API Management**.
- All five Tinybird pipes provisioned for your portal. Reprise only documents `replay_session_activity` publicly, in the [HTML Environment Data API article](https://reprise.zendesk.com/hc/en-us/articles/18940321925659). The connector reads all five, and `check` fails if any of them is missing, so confirm with Reprise support that your portal has:
  - `replay_session_activity`
  - `replay_session_summary`
  - `replay_metrics`
  - `replay_change_feed`
  - `replicate_session_activity`
- If your Airbyte deployment restricts outbound traffic, allow `app.getreprise.com` and `api.us-east.tinybird.co`.

## Set up the Reprise source

1. In the Reprise portal, go to **Settings** > **API Management**, create a token, and copy it.
2. In Airbyte, add a new **Reprise** source and paste the token into **API Token**.
3. Optionally set **Start Time** to the earliest UTC timestamp you want to backfill, in `YYYY-MM-DD HH:MM:SS` format. The connector clamps this to 18 months before the sync, and leaving it empty backfills that full 18 months.
4. Optionally set **Include Viewer PII** and **Internal email domains**. See [Viewer identity and PII](#viewer-identity-and-pii).
5. Click **Set up source**.

The token you provide is a portal key, not the credential used to read data. Before each sync, the connector posts it to `https://app.getreprise.com/api/warehouse/token` and receives a scoped warehouse JWT that is valid for 10 minutes. The connector refreshes that JWT automatically and passes it to each pipe as a `token` query parameter.

## Supported sync modes

| Feature                        | Supported? |
| ------------------------------ | ---------- |
| Full Refresh - Overwrite       | Yes        |
| Full Refresh - Append          | Yes        |
| Incremental - Append           | Yes        |
| Incremental - Append + Deduped | Yes        |

## Supported streams

| Stream | Primary key | Cursor field | Description |
| ------ | ----------- | ------------ | ----------- |
| `replay_session_activity` | `activity_id` | `since_created_at` | One row per viewer interaction in a Replay demo: guide steps, button clicks, snapshot views, plus the link and published demo the session came from. |
| `replay_session_summary` | `session_id` | `since_created_at` | One row per Replay session, with activity count, session duration, and first and last activity timestamps. |
| `replay_metrics` | `entity_type`, `entity_id`, `window_start` | `window_start` | Aggregates per entity and per sync window: distinct views, total sessions, bounce rate, mean and median session seconds, mean click and screen events. |
| `replay_change_feed` | `entity_id`, `changed_at`, `change_type` | `since_ingested_at` | Change events for Reprise entities, such as a published demo being updated. |
| `replicate_session_activity` | `session_id` | `since_created_at` | One row per Replicate session, with the demo title, shard name, and viewer classification. |

Field-level schemas come from the connector, and the `replay_session_activity` fields are described in Reprise's [HTML Environment Data API article](https://reprise.zendesk.com/hc/en-us/articles/18940321925659). Note that Tinybird returns several numeric fields as strings, so counts and durations may arrive as either a number or a string.

### Derived and dropped fields

- `replay_session_activity`, `replay_session_summary`, and `replicate_session_activity` gain a `since_created_at` field. It is the record's session timestamp normalized to `YYYY-MM-DD HH:MM:SS` and is used as the cursor.
- `replay_change_feed` gains `since_ingested_at`, the normalized `ingested_at` value.
- `replay_metrics` gains `window_start` and `window_end`, which are the boundaries of the window the connector requested rather than values returned by the API. Because `window_start` is part of the primary key, changing **Start Time** after the first sync can shift window boundaries and produce rows with new primary keys.
- `replay_session_activity` drops the `visitor_name` and `distinct_user` fields returned by the API, both of which contain viewer names or IP addresses. `visitor_email` is retained.

## Incremental syncs

All streams support incremental sync. `replay_session_activity`, `replay_session_summary`, `replay_metrics`, and `replicate_session_activity` request data in one-day windows, because Reprise caps each API response at 100 MB. Within each window, the connector pages through results 10,000 rows at a time.

Incremental runs re-request a trailing window so that late-arriving rows are picked up:

| Stream | Lookback |
| ------ | -------- |
| `replay_session_activity` | 3 days |
| `replay_session_summary` | 3 days |
| `replicate_session_activity` | 3 days |
| `replay_metrics` | 1 hour |
| `replay_change_feed` | 1 second |

Deduplication relies on the primary keys above, so use **Incremental - Append + Deduped** if you don't want the re-fetched rows duplicated in your destination.

## Viewer identity and PII

`replicate_session_activity` exposes the viewer's identity in a `viewer` field, which holds a visitor email address, or the visitor's IP address when the demo link has no welcome screen. The connector always requests this value from the API, but redacts it before emitting records:

- **Include Viewer PII** disabled (the default): `viewer` is emitted as `null`.
- **Include Viewer PII** enabled: `viewer` is emitted as returned by the API.

Regardless of that setting, the connector emits a `viewer_is_internal` boolean. It is `true` when the domain part of `viewer` matches one of the comma-separated domains in **Internal email domains**. Matching ignores case and surrounding whitespace, so a value of `Example.COM, other.io` with stray spaces still classifies `USER@example.com` and `Bob@Other.IO` as internal. If **Internal email domains** is empty, or the API returns no viewer, `viewer_is_internal` is `false`.

## Limitations and troubleshooting

- **18 months of history.** The connector clamps **Start Time** to 18 months before the sync, so it can't backfill data older than that.
- **All timestamps are UTC.** Both the configured **Start Time** and the timestamps in the data are UTC.
- **`check` tests all five streams.** If a connection check fails, the most likely cause is that one of the five pipes isn't provisioned for your portal. Ask Reprise support to confirm.
- **Rate limits.** Reprise doesn't publish rate limits. The connector retries failed requests up to five times, honoring the `Retry-After` header when the API sends one.
- **Large days.** The 100 MB response cap applies per request. A single day with an unusually high volume of activity can exceed it; in that case, narrow the sync window by raising **Start Time** for the initial backfill.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Reprise portal API key (Settings &gt; API Management). Exchanged for a scoped warehouse JWT via POST https://app.getreprise.com/api/warehouse/token before each sync. |  |
| `start_time` | `string` | Start Time. Optional UTC lower bound for full refresh / first backfill of activity, summary, replicate, change_feed, and metrics (YYYY-MM-DD HH:MM:SS). Clamped to 18 months ago. Incremental activity/summary/replicate runs only re-fetch the last 3 days (lookback_window); this sets the historical floor. |  |
| `include_viewer_pii` | `boolean` | Include Viewer PII. When enabled, replicate_session_activity emits the raw viewer column (visitor email, or IP when no welcome screen is used). Disabled by default; viewer_is_internal is always emitted. | false |
| `internal_email_domains` | `string` | Internal email domains. Comma-separated email domains treated as internal for replicate_session_activity viewer_is_internal (e.g. yourcompany.com). Requires viewer_pii from the API; raw viewer is redacted by default unless include_viewer_pii is enabled. If unset, viewer_is_internal is false for all rows. |  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-08-20 | [84883](https://github.com/airbytehq/airbyte/pull/84883) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
