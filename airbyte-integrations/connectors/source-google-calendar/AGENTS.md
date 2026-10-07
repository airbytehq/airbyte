> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-google-calendar: Unique Behaviors

Manifest-only connector (`manifest.yaml` only; no `components.py`). Base image `airbyte/source-declarative-manifest`.

## Authentication

`credentials` oneOf: `oauth2.0` ("Authenticate via Google (OAuth)" — Cloud OAuth button via `advanced_auth`, Airbyte's app, scopes `https://www.googleapis.com/auth/calendar.readonly` and `https://www.googleapis.com/auth/calendar.acls.readonly`, `extract_output: [refresh_token]`) or `manual` ("Authenticate with custom app (client ID / secret)" — the customer's own Google Cloud OAuth app). `config_normalization_rules` migrates legacy flat `client_id`/`client_secret`/`client_refresh_token_2` configs into `credentials` as `auth_type: manual` at runtime — deliberately not `oauth2.0`, so a Cloud re-authentication can't silently replace a customer-app refresh token with one from Airbyte's app.

## Per-stream reference

| Stream | Endpoint | PK | Sync modes | Cursor | Partitioned |
|---|---|---|---|---|---|
| colors | `colors` | calendar.event | full_refresh | — | no |
| settings | `users/me/settings` | id | full_refresh | — | no |
| calendarlist | `users/me/calendarList` | id | full_refresh | — | no |
| calendars | `users/me/calendarList` (returns calendarListEntry; fix planned) | id | full_refresh | — | no |
| events | `calendars/{calendar_id}/events` | id | full_refresh, incremental | `updated` → `updatedMin` request param | yes |
| acl | `calendars/{calendar_id}/acl` | calendar_id, id | full_refresh | — | yes |
| freebusy | POST `freeBusy` | calendar_id, start, end | full_refresh | — | yes |

## Partition model

A union `SubstreamPartitionRouter` (`definitions.calendar_partition_router`, `parent_key: id`, `partition_field: calendar_id`) feeds `events`/`acl`/`freebusy` from two hidden parents: `calendar_partitions` (full copy of `calendarlist`, filtered out when `calendarid` is set) and `configured_calendar_partition` (`GET calendars/{calendarid}` — resolves `primary` to the real id and works when the calendar is not in the account's list, filtered out when `calendarid` is unset). Calendar ids are URL-encoded in request paths (e.g. holiday calendars contain `#`).

## Incremental events

`events` is a `StateDelegatingStream` with `api_retention_period: P21D` over a shared `events_stream_base` (`DatetimeBasedCursor` on `updated`): a saved cursor (or no cursor — start defaults to two years ago, `day_delta(-730)`, when `start_date` is unset) older than 21 days (Google's measured cut-off is 29) clears the stale state and delegates to the full-refresh stream, which only sends `updatedMin` for a configured `start_date` inside the window; a fresh cursor delegates to the incremental stream which sends `updatedMin` directly. `state_migrations: [LegacyToPerPartitionStateMigration]` converts pre-0.2.0 global state into per-partition state. `showDeleted=true` delivers deletions as `status: "cancelled"`. Cancelled stubs carry no `updated`, so an `AddFields` with `condition: not record.get('updated')` stamps `max(stream_slice.start_time, now-1h)` so they out-date the live row under Append + Deduped. `syncToken` was rejected: opaque, non-datetime, and still requires full resync on 410.

## Error handling

`base_requester` CompositeErrorHandler order matters: 403 rate-limit predicate (`userRateLimitExceeded`/`rateLimitExceeded` → RETRY RATE_LIMITED) must precede the plain-403 config_error filter. 404 → config_error (bad `calendarid`). 410 `updatedMinTooLongAgo` → transient_error (stale bounds are dropped before they can 410, so a hit means clock/edge drift and the retry re-reads); 410 `deleted`/`fullSyncRequired` → config_error. The `acl` requester overrides with 403+404 IGNORE (non-owned calendars / missing scope). `api_budget` = 500/PT1M with `matchers: []` (empty matches all requests, including POST `freebusy`).

## Excluded resource

`channels` (watch/stop) is push-notification infrastructure, not data — intentionally not a stream.
