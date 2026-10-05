> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-google-calendar: Unique Behaviors

Manifest-only connector (`manifest.yaml` only; no `components.py`). Base image `airbyte/source-declarative-manifest`.

## Authentication

Flat OAuth fields (`client_id`, `client_secret`, `client_refresh_token_2`) feeding an `OAuthAuthenticator` refresh-token exchange against `https://oauth2.googleapis.com/token`. Tokens come from the customer's own Google Cloud OAuth app (scopes `calendar.readonly`, `calendar.acls.readonly`).

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

`DatetimeBasedCursor` on `updated`, sent as `updatedMin`. The cursor `start_datetime` defaults to `2000-01-01` when `start_date` is unset, and `updatedMin` is only sent when `stream_slice['start_time']` is newer than `day_delta(-28)` — Google rejects bounds older than ~30 days with `410 updatedMinTooLongAgo`, so stale cursors and old configured `start_date` values drop the parameter and re-read the calendar instead of failing. `state_migrations: [LegacyToPerPartitionStateMigration]` converts pre-0.3.0 global state into per-partition state. `showDeleted=true` delivers deletions as `status: "cancelled"`. `syncToken` was rejected: opaque, non-datetime, and still requires full resync on 410.

## Error handling

`base_requester` CompositeErrorHandler order matters: 403 rate-limit predicate (`userRateLimitExceeded`/`rateLimitExceeded` → RETRY RATE_LIMITED) must precede the plain-403 config_error filter. 404 → config_error (bad `calendarid`). 410 → config_error (defensive; stale `events` bounds are dropped before they can 410, so the message directs the user to fix or clear Start Date). The `acl` requester overrides with 403+404 IGNORE (non-owned calendars / missing scope). `api_budget` = 500/PT1M with `matchers: []` (empty matches all requests, including POST `freebusy`).

## Excluded resource

`channels` (watch/stop) is push-notification infrastructure, not data — intentionally not a stream.
