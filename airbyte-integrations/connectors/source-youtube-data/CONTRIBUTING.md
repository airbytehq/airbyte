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
