> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-google-calendar: Unique Behaviors

Manifest-only connector (`manifest.yaml` only; no `components.py`). Base image `airbyte/source-declarative-manifest`.

## Authentication

Flat OAuth fields (`client_id`, `client_secret`, `client_refresh_token_2`) feeding an `OAuthAuthenticator` refresh-token exchange against `https://oauth2.googleapis.com/token`. Tokens come from the customer's own Google Cloud OAuth app (scopes `calendar.readonly`, `calendar.acls.readonly`).

## Per-stream reference

| Stream | Endpoint | PK | Sync modes | Cursor | Partitioned |
| --- | --- | --- | --- | --- | --- |
| colors | `colors` | kind | full_refresh | — | no |
| settings | `users/me/settings` | id | full_refresh | — | no |
| calendarlist | `users/me/calendarList` | id | full_refresh | — | no |
| calendars | `calendars/{calendar_id}` | id | full_refresh | — | yes, readable listed calendars |
| events | `calendars/{calendar_id}/events` | calendar_id, id | full_refresh, incremental | `updated` → `updatedMin` request param | yes |
| acl | `calendars/{calendar_id}/acl` | calendar_id, id | full_refresh | — | yes |
| freebusy | POST `freeBusy` | calendar_id, start, end | full_refresh | — | yes |

## Partition model

Three `SubstreamPartitionRouter`s (`parent_key: id`, `partition_field: calendar_id`) feed `events`/`acl`/`freebusy` from the same hidden parent, `calendar_partitions`. With `calendarid` set, the parent uses `GET calendars/{calendarid}` — resolves `primary` to the real id and works when the calendar is not in the account's list. Otherwise it pages through `users/me/calendarList` with `showHidden=true` and `minAccessRole=reader` for events (`readable_calendar_partition_router`), `owner` for ACL (`owned_calendar_partition_router`), or no minimum for freebusy (`calendar_partition_router`). Role filters are omitted for an explicitly configured calendar. A `RecordExpander` emits list items or the single calendar response; records without an id are filtered out. Calendar ids are URL-encoded in request paths (e.g. holiday calendars contain `#`). The public `calendars` stream independently reads every listed calendar with `minAccessRole=reader` and `showHidden=true`, regardless of `calendarid`; it returns calendar resources, not calendar-list entries.

## Incremental events

`events` is a `StateDelegatingStream` with `api_retention_period: P21D` over a shared `events_stream_base` (`DatetimeBasedCursor` on `updated`): a saved cursor older than 21 days (Google's measured cut-off is 29), or no usable saved state, delegates to the full-refresh stream. Without `start_date`, the cursor starts at `2000-01-01T00:00:00Z`. The full-refresh stream filters client-side and only sends `updatedMin` for a configured `start_date` within the last 21 days; a fresh cursor delegates to the incremental stream which sends `updatedMin` directly. `global_substream_cursor: true` keeps a single cursor across all calendar partitions, so the retention check and every partition's `updatedMin` use the same value. The flat 0.1.0 state is not carried over: the first sync after upgrading re-reads, without a state migration component. `showDeleted=true` delivers deletions as `status: "cancelled"`. Cancelled stubs without `updated` get an `AddFields` stamp of `max(stream_slice.start_time, now-1h)` so they out-date the live row under Append + Deduped. `singleEvents=false` keeps recurring series unexpanded. `syncToken` is not used.

## Error handling

`base_requester` CompositeErrorHandler order matters: 401 → config_error (re-authorize or generate a new refresh token); `userRateLimitExceeded`/`rateLimitExceeded` → RATE_LIMITED; `quotaExceeded`/`dailyLimitExceeded` except HTTP 429 → transient_error (wait for quota reset), all before the plain-403 config_error filter (access denied or disabled API). 404 → config_error (check the configured ID or a removed listed calendar). 410 `deleted`/`fullSyncRequired` → config_error (check ID and reset events); other 410 responses → transient_error with a message that the next sync re-reads automatically. HTTP 429 → RATE_LIMITED; 500/502/503/504 → RETRY, with exponential backoff factor 5. The `acl` requester checks credentials, rate limits and quota first, then missing scope/disabled API → config_error with instructions to generate a scoped refresh token or deselect ACL; other 403 and 404 responses → IGNORE. The `freebusy` requester logs calendar-level errors in successful responses and emits no rows; plain 403 → config_error. Its window is now minus 30 days to now plus 45 days, ignoring `start_date`. `api_budget` = 500/PT1M with `matchers: []` (all requests, including POST `freeBusy`). Concurrency defaults to 3, maximum 10.

## Excluded resource

`channels` (watch/stop) is push-notification infrastructure, not data — intentionally not a stream.
