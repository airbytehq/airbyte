> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-youtube-data: Unique Connector Behaviors

This connector is manifest-only (`language:manifest-only`, `cdk:low-code`); all behavior below lives in `manifest.yaml` and there is no `components.py`. `README.md` is a symlink to the shared declarative-source README, so connector-specific notes belong here.

It wraps the [YouTube Data API v3](https://developers.google.com/youtube/v3) and exposes five streams: `channels`, `videos`, `video`, `comments`, `channel_comments`. For channel and content-owner analytics reports, the manifest description already points users to [source-youtube-analytics](https://docs.airbyte.com/integrations/sources/youtube-analytics).

## 1. Every stream is full refresh

The manifest declares no `incremental_sync` and no `DatetimeBasedCursor`, so all five streams re-read everything on every sync. The single `cursor_field: channel_id` in the manifest belongs to the `channels` `ListPartitionRouter` — it names the partition field, not a state cursor, and nothing is persisted between syncs.

The YouTube Data API list endpoints used here (`channels.list`, `videos.list`, `commentThreads.list`) accept no date filter at all. `search.list` does accept `publishedAfter`/`publishedBefore`, but those filter on video publish time, not on last modification, and the fields this connector cares about (statistics, comments, channel branding) mutate continuously after publication — so a publish-time cursor would silently freeze counters at their first-seen values.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| channels | small | top-level parent | none | none | deferred_no_api_support | `channels.list` has no date filter; one record per configured channel ID |
| videos | large | top-level parent | none | created_at_only | deferred_no_api_support | `search.list` supports `publishedAfter`/`publishedBefore` (publish time only); records are ID objects, so there is no timestamp in the record to checkpoint on |
| video | large | child | none | none | deferred_child | `videos.list` is an ID lookup; partitions come from `videos` |
| comments | xlarge | child | none | none | deferred_child | `commentThreads.list` has no date filter; comments are mutable (edits, likes, deletions) |
| channel_comments | xlarge | top-level parent | none | none | deferred_no_api_support | Same `commentThreads.list` limitation, keyed on the channel instead of a video |

Incremental options for this connector are tracked in [airbyte-internal-issues#17103](https://github.com/airbytehq/airbyte-internal-issues/issues/17103).

**Why this matters:** Each sync replays the full history for every stream, which multiplies both destination write volume and YouTube quota consumption (see section 6). Do not add a cursor on `publishedAt` or on the synthetic `datetime` field (section 4) as a shortcut — the first would drop updates to already-synced videos, and the second is not a source timestamp at all.

## 2. `videos` emits search result IDs, not video resources

The `videos` stream requests `search` and its `DpathExtractor` selects `items` → `*` → `id`, so each record is the search result's ID object — `{"kind": ..., "videoId": ...}` — rather than a video resource. The inline schema matches that shape and declares only `kind` and `videoId`.

Two consequences follow from the request itself. The request sets only `channelId` and `maxResults`, with no `type=video`, so `search.list` also returns channel and playlist results, whose ID objects carry `channelId` or `playlistId` instead of `videoId`. And `search.list` caps the total result set the API will page through, so `videos` is not a reliable full inventory of a channel's uploads.

This thin-record behavior is an open defect under investigation in [airbyte-internal-issues#17100](https://github.com/airbytehq/airbyte-internal-issues/issues/17100). Treat it as current observed behavior, not as intended design: `videos` is currently useful mainly as the partition source for `video` and `comments` (section 3), and per-video metadata is available in the `video` stream.

**Why this matters:** Users selecting `videos` expecting video metadata get two ID fields. Any change here is user-visible — widening the extractor to `items.*` would change the stream's schema and record shape, so route it through [#17100](https://github.com/airbytehq/airbyte-internal-issues/issues/17100) and the breaking-change process rather than treating it as a bug fix.

## 3. `video` and `comments` partitions are silently dropped when the parent record has no `videoId`

Both `video` and `comments` use a `SubstreamPartitionRouter` over `videos` with `parent_key: videoId`. The CDK resolves that key with `dpath` and, when the key is absent from a parent record, skips the partition without emitting a log line. Combined with section 2 — `search.list` returning channel and playlist results that have no `videoId` — some parent records produce no child requests at all, and nothing in the sync output says so.

**Why this matters:** A `video` or `comments` record count lower than the `videos` record count is expected behavior here, not evidence of a sync failure. When debugging apparent data loss in these streams, compare the parent records' `kind` values first; adding `type=video` to the `videos` request would be the targeted fix, but it changes which records `videos` returns and therefore needs the same breaking-change evaluation as section 2.

## 4. `video.datetime` is an extraction timestamp, not a YouTube timestamp

The `video` stream has an `AddFields` transformation that sets `datetime` to `{{ now_utc() }}`, evaluated while the record is being processed. The inline schema types it `[string, "null"]` with no `format`, and no `format: date-time` appears anywhere in the manifest — including on real API timestamps such as `publishedAt`. The value therefore reaches destinations as an unconstrained string whose textual form comes from the CDK's `now_utc()` rendering rather than from a normalized ISO-8601 serializer.

The same stream also flattens `snippet` into the record root (`DpathFlattenFields` with `delete_origin_value: true`) and re-adds `videoId` from the partition value, so the record shape does not match the raw `videos.list` response.

Field-typing and key concerns for this connector are tracked in [airbyte-internal-issues#17091](https://github.com/airbytehq/airbyte-internal-issues/issues/17091).

**Why this matters:** `datetime` answers "when did Airbyte read this row", not "when did anything happen on YouTube" — using it as an event time or as a sync cursor produces wrong analytics. Because it is declared as a plain string, destinations land it as text rather than a timestamp; changing its type or format is a schema change and needs a breaking-change evaluation.

## 5. Three of five streams declare no primary key

`primary_key` is declared only on `video` (`videoId`) and `channels` (`id`). `videos`, `comments`, and `channel_comments` have none, so destinations cannot deduplicate them and full-refresh appends accumulate duplicates across syncs.

For the two comment streams this is a consequence of extraction rather than a missing API field: both request `part: snippet,replies` but extract `items` → `*` → `snippet`, which discards the comment thread's own `id` (and the `replies` object the request paid quota for). A stable identifier does survive nested at `topLevelComment.id`. `videos` carries `videoId` in every video-kind record but does not declare it as a key — and could not do so safely today, since channel- and playlist-kind records lack that field entirely (section 2).

**Why this matters:** Declaring a primary key on any of these streams is a schema change requiring the breaking-change process, and for the comment streams it would first require widening extraction. Track this under [#17091](https://github.com/airbytehq/airbyte-internal-issues/issues/17091) rather than adding keys ad hoc.

## 6. No error handler, so quota exhaustion surfaces unclassified

The manifest contains no `error_handler`, `DefaultErrorHandler`, or `HttpResponseFilter` for any stream. YouTube signals quota exhaustion with HTTP 403 and a `quotaExceeded` reason, which without a response filter is not classified as a rate-limit or transient condition and surfaces as a generic request failure.

The exposure is real rather than theoretical: `search.list`, used by `videos`, costs 100 quota units per call (see the [quota calculator](https://developers.google.com/youtube/v3/determine_quota_cost)) against a default project allocation of [10,000 units per day](https://developers.google.com/youtube/v3/getting-started#quota), and every extra page of results costs another 100. The other endpoints used here cost 1 unit per call. Since nothing is incremental (section 1), a full sync pays the `videos` cost again every time.

Error classification for this connector is tracked in [airbyte-internal-issues#17094](https://github.com/airbytehq/airbyte-internal-issues/issues/17094).

**Why this matters:** A quota-exhausted sync fails with a message that does not mention quota, so the same failure is easy to misdiagnose as an auth or configuration problem. When triaging a 403 here, check the response body's `reason` before touching credentials. Adding an `HttpResponseFilter` that maps `quotaExceeded` to a rate-limit error with a clear message is the natural fix, and it is not breaking.

## 7. `channel_ids` is a list, but only `channels` fans out over it

The `channel_ids` config field is an array. Only the `channels` stream consumes it as a list, via a `ListPartitionRouter` that issues one request per ID. `videos` interpolates `channelId: "{{ config.channel_ids }}"` and `channel_comments` interpolates `allThreadsRelatedToChannelId: "{{ config.channel_ids }}"` — both are single-value YouTube request parameters receiving a rendered list.

This matches the multiple-channel-ID breakage reported in [airbytehq/airbyte#72638](https://github.com/airbytehq/airbyte/issues/72638). Note also that `check` exercises only the `channels` stream, so a successful connection check does not prove the other four streams can build valid requests for the configured IDs.

**Why this matters:** Multi-channel configurations are only trustworthy for `channels` today; the video and comment streams need `ListPartitionRouter` fan-out (or per-ID partitioning) to behave correctly, and until then a passing check can mask the problem.

## Fivetran parity

Certification register item V-1. [Fivetran's YouTube Analytics connector](https://fivetran.com/docs/connectors/applications/youtube-analytics) syncs from two different Google APIs, and the parity verdict differs by group: its Reporting API tables belong to `source-youtube-analytics`, while its Data API metadata tables overlap this connector directly and are assessed row by row.

| Fivetran table group | Fivetran source API | This connector | Verdict | Reason |
|---|---|---|---|---|
| Channel reports (for example `CHANNEL_BASIC_A2`) | Reporting API | none | Out of scope | Aggregated analytics reports delivered through reporting jobs; covered by [source-youtube-analytics](https://docs.airbyte.com/integrations/sources/youtube-analytics), which the manifest description points users to |
| Content owner reports | Reporting API | none | Out of scope | Requires a content owner ID and content-owner-scoped reporting jobs; belongs to `source-youtube-analytics` |
| Audience retention reports | Reporting API (targeted queries) | none | Out of scope | Retention curves are an analytics report type, not a Data API resource |
| `SYSTEM_MANAGED_*` revenue and asset tables | Reporting API (system-managed) | none | Out of scope | Content-owner-only revenue, claim, and asset snapshots; not exposed by the Data API |
| Channels metadata | Data API `channels.list` | `channels` | Parity | Same endpoint; this connector requests a broader `part` list (`snippet`, `contentDetails`, `statistics`, `brandingSettings`, `topicDetails`, `status`, `localizations`, `contentOwnerDetails`) |
| Videos metadata | Data API `videos.list` | `video` (+ `videos` for IDs) | Partial | `video` returns full `videos.list` metadata, but only for IDs discovered through `search.list`, which is capped and mixes in non-video results (sections 2 and 3). Fivetran instead requests all accessible uploads and re-requests metadata for videos uploaded since one month before the last sync; this connector is full refresh only (section 1) |
| Comments metadata | Data API `commentThreads`/`comments` | `comments`, `channel_comments` | Partial | Both streams cover comment threads, but extraction keeps only `snippet`, dropping the thread `id` and the `replies` payload (section 5) |
| Captions metadata | Data API `captions.list` | none | Gap | No `captions` stream exists; a `captions.list` stream partitioned on video IDs would be a straightforward declarative addition |
| Playlists metadata | Data API `playlists.list` | none | Gap | No `playlists` stream exists, even though `search.list` already returns playlist IDs that are currently discarded (section 2) |

**Why this matters:** The Reporting API rows are a deliberate product boundary — do not close them by adding report streams here. The two gap rows (`captions`, `playlists`) are genuine coverage gaps that a declarative stream addition could close, and the two partial rows are consequences of the extraction and discovery defects above rather than independent work items.
