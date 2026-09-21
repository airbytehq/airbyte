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

`DatetimeBasedCursor` on `updated`, sent as `updatedMin`. The cursor `start_datetime` defaults to a `2000-01-01` sentinel when `start_date` is unset, and `updatedMin` is only sent when `stream_slice['start_time'] > '2001-01-01'` — so full refresh and first incremental syncs fetch all events; saved cursors and configured `start_date` are honored. Google rejects `updatedMin` older than ~30 days with `410 updatedMinTooLongAgo` (a paused connection beyond that window needs an events reset). `state_migrations: [LegacyToPerPartitionStateMigration]` converts pre-0.3.0 global state into per-partition state. `showDeleted=true` delivers deletions as `status: "cancelled"`. `syncToken` was rejected: opaque, non-datetime, and still requires full resync on 410.

## Error handling

`base_requester` CompositeErrorHandler order matters: 403 rate-limit predicate (`userRateLimitExceeded`/`rateLimitExceeded` → RETRY RATE_LIMITED) must precede the plain-403 config_error filter. 404 → config_error (bad `calendarid`). 410 → system_error (stale `events` cursor → reset). The `acl` requester overrides with 403+404 IGNORE (non-owned calendars / missing scope). `api_budget` = 500/PT1M with `matchers: []` (empty matches all requests, including POST `freebusy`).

## Excluded resource

`channels` (watch/stop) is push-notification infrastructure, not data — intentionally not a stream.
