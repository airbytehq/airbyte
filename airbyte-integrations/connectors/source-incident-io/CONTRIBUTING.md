# source-incident-io: contributor notes

## Authentication

incident.io offers API-key (HTTP bearer) authentication only. There is no OAuth flow to implement:
the vendor OpenAPI document (https://api.incident.io/v1/openapiV3.json) declares a single
`components.securitySchemes.BearerAuth` scheme. Keys are created under Settings > API keys and can be
scoped; a key missing a scope gets a `403` whose body names the scope, and the connector's error
handler surfaces that message to the user.

## `incident_mode` partition router on `actions` and `follow-ups`

The `/v3/actions` and `/v3/follow_ups` endpoints only return records from `standard` and `retrospective` incidents when `incident_mode` is not set. The deprecated `/v2` endpoints returned records from every incident mode, so a plain `/v3` request drops records (on one internal account: 91 of 224 actions and 22 of 602 follow-ups).

To keep parity with `/v2`, both streams use a `ListPartitionRouter` that sends one request series per documented `incident_mode` value: `standard`, `retrospective`, `test`, `tutorial`, `stream`. Each record belongs to exactly one mode, so the partitions do not overlap.

If incident.io adds a new `incident_mode` value (see the `incident_mode` parameter in https://docs.incident.io/openapi/latest.json), add it to the `values` list of both routers in `manifest.yaml` and to `_MODES` in `unit_tests/test_v3_streams.py`. Otherwise records from incidents in that mode will silently stop syncing.

## Incremental sync sends dates, not timestamps

`incidents`, `alerts`, `escalations`, `actions` and `follow-ups` are incremental on `updated_at`. The
API's `updated_at[gte]` filter accepts a date only: a timestamp such as `2026-09-18T10:38:16Z` is
rejected with `422 Filter field date_range must provide a date in the format yyyy-mm-dd` (verified
against the live API on 2026-10-06). The shared `updated_at_cursor` therefore keeps the full timestamp
in state but formats the slice start as `%Y-%m-%d` in `request_parameters`. Every sync re-reads the
records updated since midnight UTC of the day the state points to; those are de-duplicated by primary
key when the destination sync mode is Append + Deduped (with plain Append they are kept). Do not switch to `start_time_option` with a full-timestamp `datetime_format`,
and do not enable client-side filtering: the day-level overlap is what prevents gaps at the boundary.

Record timestamps come back as `%Y-%m-%dT%H:%M:%S.%fZ`; older reports (airbytehq/alpha-beta-issues issues
1769 and 2926) show `%Y-%m-%dT%H:%M:%SZ` as well, so both are listed in `cursor_datetime_formats`.

**The cursor window applies to full-refresh syncs too.** A declarative stream with a
`DatetimeBasedCursor` sends `updated_at[gte]` whatever the sync mode, so the default `start_date` has
to predate all incident.io data. It is `2020-01-01`. A regression run
with a two-year default lost every 2023 record on an existing full-refresh connection; do not make the
default relative to "now".

## Page sizes

Each paginated stream uses the largest `page_size` the API serves (`incidents` 250,
`incident_updates` 250, `users` 10000, `alerts` 50, `escalations` 50, `actions` and `follow-ups` 250).
For `incidents` the OpenAPI spec allows 500, but the API caps it at 250: a request for 500 comes back
with `pagination_meta.page_size: 250`. One exception: `schedules` stays at 100 because the vendor
documents that `next_shifts` is only
returned when `page_size` is 25 or lower, and the connector does not emit `next_shifts` today. Lower it
to 25 if that field is ever added to the schema.

## Rate limits and errors

The API key allows 1,200 requests per minute, but `GET /v2/incidents` is bound at 60 per minute: its
`x-ratelimit-limit` header reads `60, 1200;window=60, 60;window=60` while every other endpoint reads
`1200, 1200;window=60` (checked live on 2026-10-07). The `api_budget` therefore has two policies, matched
in order: 60/min for `/v2/incidents`, 1,200/min for everything else. It also reads
`x-ratelimit-remaining` so a zero from the API drains the local bucket. `x-ratelimit-reset` is not
declared on purpose: with a `MovingWindowCallRatePolicy` the CDK only syncs the bucket when no reset
header is present. A `429` is retried after the `retry-after` header (the vendor says to prefer it).
`401` and `403` are configuration errors with actionable messages; `408` and `5xx` are retried; other
`4xx` fail as system errors with the vendor's message. The message templates read
`(response.get('errors') or [{}])[0].get('message', ...)`: the `or` matters, an empty `errors` list
would otherwise raise inside the error handler and turn a clear configuration error into a generic one.

## `users` includes deactivated accounts

`users` sends `include_inactive=true` so deactivated or not-yet-active users are present, with the
vendor's `is_active` flag declared in the schema. Without it, a user who leaves the organisation
disappears from the stream.
