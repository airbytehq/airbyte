# Contributing to source-youtube-data

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This connector is manifest-only, so all behavior lives in `manifest.yaml`. `README.md` is a symlink to the shared declarative-source README; connector-specific notes go in [AGENTS.md](./AGENTS.md), which is the canonical, detailed version of everything summarized below.

## 1. Every stream is full refresh

None of the five streams (`channels`, `videos`, `video`, `comments`, `channel_comments`) is incremental, so every sync re-reads everything. The `cursor_field: channel_id` in the manifest is a partition field on `channels`, not sync state.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| channels | small | top-level parent | none | none | deferred_no_api_support | `channels.list` has no date filter; one record per configured channel ID |
| videos | large | top-level parent | none | created_at_only | deferred_no_api_support | `search.list` supports `publishedAfter`/`publishedBefore` (publish time only); records are ID objects, so there is no timestamp in the record to checkpoint on |
| video | large | child | none | none | deferred_child | `videos.list` is an ID lookup; partitions come from `videos` |
| comments | xlarge | child | none | none | deferred_child | `commentThreads.list` has no date filter; comments are mutable (edits, likes, deletions) |
| channel_comments | xlarge | top-level parent | none | none | deferred_no_api_support | Same `commentThreads.list` limitation, keyed on the channel instead of a video |

Incremental options are tracked in [airbyte-internal-issues#17103](https://github.com/airbytehq/airbyte-internal-issues/issues/17103).

## 2. `videos` emits search result IDs, not video resources

The `videos` stream extracts only each search result's ID object, so records contain just `kind` and `videoId` instead of video metadata. This is an open defect tracked in [airbyte-internal-issues#17100](https://github.com/airbytehq/airbyte-internal-issues/issues/17100), not intended design — per-video metadata comes from the `video` stream.

## 3. `video` and `comments` partitions are silently dropped when the parent record has no `videoId`

Both streams partition over `videos` on `videoId`, and the CDK skips parent records that lack that key without logging. Because the `videos` request does not restrict `search.list` to videos, channel and playlist results produce no child requests at all.

## 4. `video.datetime` is an extraction timestamp, not a YouTube timestamp

`video.datetime` is generated with `{{ now_utc() }}` when the record is processed and is typed as a plain string with no `date-time` format. Do not treat it as an event time or use it as a cursor.

## 5. Three of five streams declare no primary key

Only `video` and `channels` declare a primary key; `videos`, `comments`, and `channel_comments` have none, so destinations cannot deduplicate them. For the comment streams this is because extraction keeps only `snippet` and discards the thread `id`. Tracked in [airbyte-internal-issues#17091](https://github.com/airbytehq/airbyte-internal-issues/issues/17091).

## 6. No error handler, so quota exhaustion surfaces unclassified

The manifest defines no error handler, so YouTube's HTTP 403 `quotaExceeded` response is not classified as a rate limit and fails the sync with a message that never mentions quota. `search.list` costs 100 of the default [10,000 daily quota units](https://developers.google.com/youtube/v3/getting-started#quota) per page. Tracked in [airbyte-internal-issues#17094](https://github.com/airbytehq/airbyte-internal-issues/issues/17094).

## 7. `channel_ids` is a list, but only `channels` fans out over it

Only `channels` issues one request per configured channel ID; `videos` and `channel_comments` interpolate the whole array into single-value request parameters, which matches the breakage reported in [airbytehq/airbyte#72638](https://github.com/airbytehq/airbyte/issues/72638). The connection check only exercises `channels`, so it can pass while the other streams are broken.

## Fivetran parity

[Fivetran's YouTube Analytics connector](https://fivetran.com/docs/connectors/applications/youtube-analytics) syncs both YouTube Reporting API reports and YouTube Data API metadata. The report tables are out of scope here and belong to [source-youtube-analytics](https://docs.airbyte.com/integrations/sources/youtube-analytics); the Data API metadata tables overlap this connector and are assessed individually below.

| Fivetran table group | Fivetran source API | This connector | Verdict | Reason |
|---|---|---|---|---|
| Channel reports (for example `CHANNEL_BASIC_A2`) | Reporting API | none | Out of scope | Aggregated analytics reports; covered by `source-youtube-analytics` |
| Content owner reports | Reporting API | none | Out of scope | Requires a content owner ID; belongs to `source-youtube-analytics` |
| Audience retention reports | Reporting API (targeted queries) | none | Out of scope | Analytics report type, not a Data API resource |
| `SYSTEM_MANAGED_*` revenue and asset tables | Reporting API (system-managed) | none | Out of scope | Content-owner-only revenue and asset snapshots; not exposed by the Data API |
| Channels metadata | Data API `channels.list` | `channels` | Parity | Same endpoint, with a broader `part` list |
| Videos metadata | Data API `videos.list` | `video` (+ `videos` for IDs) | Partial | Limited to IDs discovered via `search.list`, and full refresh only |
| Comments metadata | Data API `commentThreads`/`comments` | `comments`, `channel_comments` | Partial | Extraction keeps only `snippet`, dropping the thread `id` and `replies` |
| Captions metadata | Data API `captions.list` | none | Gap | No `captions` stream exists |
| Playlists metadata | Data API `playlists.list` | none | Gap | No `playlists` stream exists |

See [AGENTS.md](./AGENTS.md) for the full reasoning behind each verdict.
