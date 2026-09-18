> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-google-calendar: Unique Behaviors

Manifest-only connector (`manifest.yaml` only; no `components.py`). Base image `airbyte/source-declarative-manifest`.

## Authentication

`credentials` oneOf: `oauth2.0` (Cloud OAuth button via `advanced_auth`, scope `https://www.googleapis.com/auth/calendar.readonly`, `extract_output: [refresh_token]`) or `manual` refresh token. `config_normalization_rules` migrates legacy flat `client_id`/`client_secret`/`client_refresh_token_2` configs into `credentials` at runtime.

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

`definitions.streams.calendar_partitions` is a hidden full copy of `calendarlist` (not in top-level `streams:`) with a `record_filter` honoring optional `calendarid` (and `primary` via the `primary` flag on the entry). `events`/`acl`/`freebusy` use a `SubstreamPartitionRouter` with `parent_key: id`, `partition_field: calendar_id`. Do not `$ref`+override the parent stream — sibling overrides replace the whole `retriever` dict; keep the full copy.

## Incremental events

`DatetimeBasedCursor` on `updated`, sent as `updatedMin`. `start_date` defaults to ~25 days ago because Google rejects `updatedMin` older than ~30 days with `410 updatedMinTooLongAgo`. `state_migrations: [LegacyToPerPartitionStateMigration]` converts pre-0.3.0 global state into per-partition state. `showDeleted=true` delivers deletions as `status: "cancelled"`. `syncToken` was rejected: opaque, non-datetime, and still requires full resync on 410.

## Error handling

`base_requester` CompositeErrorHandler order matters: 403 rate-limit predicate (`userRateLimitExceeded`/`rateLimitExceeded`/`quotaExceeded` → RETRY RATE_LIMITED) must precede the plain-403 config_error filter. 404 → config_error (bad `calendarid`). 410 → system_error (stale `events` cursor → reset). The `acl` requester overrides with 403+404 IGNORE (non-owned calendars / missing scope). `api_budget` = 500/PT1M with `matchers: []` (empty matches all requests, including POST `freebusy`).

## Excluded resource

`channels` (watch/stop) is push-notification infrastructure, not data — intentionally not a stream.
