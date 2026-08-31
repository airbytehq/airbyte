> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-youtube-data

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

All five streams are currently full-refresh-only. The YouTube Data API v3 exposes usable cursors on only part of the surface, and where they exist the stream's current record shape does not yet carry the cursor field. The table records the per-stream reasoning.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| channels | small | top-level parent (config `channel_ids`) | none | none | full_refresh_only | `channels.list` by ID has no date filter; channel records are mutable config-style lookups. |
| videos | medium | top-level parent | none in record | `publishedAfter` on `search.list` | deferred_needs_record_reshape | The endpoint supports `publishedAfter`, but the extractor keeps only `items[].id` (`kind`, `videoId`) — the record carries no date to cursor on. Incremental requires first reshaping records to include `snippet.publishedAt` (tracked as the thin-record investigation), then a `DatetimeBasedCursor` on it. Note `publishedAt` is creation-time only: edits to a video do not move it, so a lookback or periodic full refresh is still needed for updated metadata. |
| video | medium | substream of `videos` | none | none | full_refresh_only | `videos.list` by ID has no date-based filtering; it fetches whatever IDs the parent supplies. Statistics fields (view/like counts) change constantly, so even with a cursor the data is inherently mutable. |
| comments | medium | substream of `videos` | none top-level | none server-side | deferred_client_side_candidate | `commentThreads.list` has no date filter. Records carry `topLevelComment.snippet.publishedAt` and `updatedAt` (comments are editable, so `updatedAt` is the correct cursor), but both are nested; client-side incremental requires hoisting the cursor to the top level first. |
| channel_comments | medium | top-level parent (config `channel_ids`) | none top-level | none server-side | deferred_client_side_candidate | Same shape and reasoning as `comments`. |

## Primary keys

- `videos` records are `search.list` id objects; `videoId` is the key.
- `comments` / `channel_comments` records are commentThread snippets, which do not include the thread id at the top level. The connector hoists `topLevelComment.id` (equal to the thread id in the YouTube API) into a top-level `id` via an `AddFields` transformation, and keys the streams as composites with their parent context: `[videoId, id]` and `[channelId, id]` respectively.

## Error handling

All five streams share the error handler defined on `definitions.base_requester` in `manifest.yaml`. YouTube reports its error taxonomy in two places, and the filters check both: legacy reasons in `error.errors[0].reason` and modern reasons in `error.details[0].reason`.

| Response | Action | Failure type | Rationale |
|---|---|---|---|
| `commentsDisabled`, `videoNotFound` | IGNORE | — | Per-video conditions on the comment streams: a video with comments disabled, or deleted between the parent fetch and the child request, is an empty partition, not an error. |
| 401 | FAIL | `config_error` | Expired or revoked OAuth grant; re-authenticate. |
| `keyInvalid` / `API_KEY_INVALID`, `accessNotConfigured` / `SERVICE_DISABLED`, `channelNotFound`, `ACCESS_TOKEN_SCOPE_INSUFFICIENT` | FAIL | `config_error` | User-correctable: invalid key, YouTube Data API v3 not enabled in the Google Cloud project, wrong Channel IDs, or missing OAuth scope. Surfaces Google's own message plus remediation steps. |
| `quotaExceeded`, `dailyLimitExceeded`, `rateLimitExceeded`, `userRateLimitExceeded` / `RATE_LIMIT_EXCEEDED`, `QUOTA_EXCEEDED` (all arrive as 403, not 429) | RETRY | `transient_error` | Quota-metered API: per-minute limits recover within the retry budget; the daily quota does not, and the sync fails as transient after retries are exhausted (quota resets midnight Pacific). |
| 429, 500, 502, 503, 504 | RETRY | `transient_error` | Standard transient classification with exponential backoff. |
| Any other error response | FAIL (terminal) | `system_error` | CDK `DefaultErrorHandler` fallback. An explicit catch-all filter is deliberately omitted because `HttpResponseFilter` predicates are evaluated against every response, including HTTP 200s. |

## Quota model

The YouTube Data API v3 grants a default quota of 10,000 units per day per Google Cloud project. Costs differ by endpoint: `search.list` costs 100 units per call (each pagination page is another call), while `channels.list`, `videos.list`, and `commentThreads.list` cost 1 unit. Exhausting the daily quota is the documented failure mode for this API: Google returns HTTP 403 with reason `quotaExceeded`, and the quota resets at midnight Pacific.

The manifest declares an `api_budget` sized to this model: `search.list` is capped at 3 calls per hour (≤ 7,200 units/day) and the 1-unit endpoints at 90 calls per hour (≤ 2,160 units/day), bounding a connection at roughly 9,400 units/day. Hourly windows were chosen deliberately: the budget makes requests wait for a free slot, and a one-hour window keeps the worst-case wait below the 5400-second heartbeat (`maxSecondsBetweenMessages`). The trade-off is backfill speed — a channel with many videos pages `search.list` at 3 pages/hour.

## Known record-shape quirks

- **`videos` records are thin**: the stream reads `search.list` and keeps only the id object (`kind`, `videoId`). It exists primarily as the parent for `video` and `comments`. The request pins `type=video`, since search otherwise also returns channel and playlist hits whose id objects carry no `videoId`.
- **`video.datetime` is connector-synthesized**: an `AddFields` stamp of the sync time (`now_utc().isoformat()`, ISO-8601), not an API field. It changes on every sync by construction.

## Competitor parity (Fivetran)

Fivetran's YouTube coverage is [YouTube Analytics](https://fivetran.com/docs/connectors/applications/youtube-analytics), built on the YouTube **Analytics** API. This connector reads the YouTube **Data** API v3 — a different API surface (content metadata and comments, not performance reporting). Row-by-row verdicts:

| Fivetran table (YouTube Analytics) | Verdict | Reason |
|---|---|---|
| Channel performance reports (views, watch time, subscriber deltas) | out-of-scope | Analytics API report; not exposed by the Data API. `channels.statistics` carries only current totals (view/subscriber/video counts), not time-series. |
| Video performance reports (views, watch time, retention) | out-of-scope | Analytics API report; `video.statistics` carries only current totals. |
| Playlist performance reports | out-of-scope | Analytics API report; this connector has no playlist streams. |
| Demographics / traffic-source / device reports | out-of-scope | Analytics API dimensions with no Data API counterpart. |
| Channel metadata | covered | `channels` (snippet, statistics totals, branding, status, topics). |
| Video metadata | covered | `video` (snippet, contentDetails, statistics totals, player, status), keyed per configured channel via `videos`. |
| Comments | covered | `comments` (per video) and `channel_comments` (all threads for a channel) — no Fivetran counterpart; this connector exceeds parity here. |

Users needing the Analytics report tables should use the separate [YouTube Analytics connector](https://docs.airbyte.com/integrations/sources/youtube-analytics), which reads the Analytics API.

## Breaking-change assessment (0.1.0)

Three 0.1.0 changes trip the breaking-change checklist and are declared in `metadata.yaml` `releases.breakingChanges` with a [migration guide](https://docs.airbyte.com/integrations/sources/youtube-data-migrations):

- **Primary keys added** on `comments`, `videos`, `channel_comments` (with a new hoisted `id` field on the comment streams) — changes dedup behavior in destinations.
- **`format: date-time` added to nine timestamp fields** — destinations that map JSON-schema formats change column types; data-lake destinations may need table recreation.
- **`videos` pins `type=video`** — the stream stops returning channel/playlist id records it previously emitted (those records carried a null `videoId` and broke the new primary key).

The 0.0.65 → 0.1.0 minor bump is the breaking magnitude for a pre-1.0 connector.
