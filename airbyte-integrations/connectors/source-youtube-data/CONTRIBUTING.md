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
