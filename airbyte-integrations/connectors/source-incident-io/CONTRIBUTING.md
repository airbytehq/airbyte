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

## `incidents` includes every status category

`GET /v2/incidents` leaves out `declined`, `canceled` and `merged` incidents unless `status_category` is set. In a sandbox check, the default request returned 9 incidents and a request for all eight categories returned 12.

The `incidents` requester in `manifest.yaml` sends all eight categories as repeated `status_category[one_of]` parameters: `triage`, `live`, `learning`, `paused`, `closed`, `declined`, `canceled` and `merged`.

If incident.io adds a status category, add it to that list and to `_STATUS_CATEGORIES` in `unit_tests/test_v3_streams.py`; otherwise those incidents will silently stop syncing.

## Incremental sync reads `updated_at` in `date_range` windows

`incidents`, `alerts`, `escalations`, `actions` and `follow-ups` are incremental on `updated_at`.
Sending `updated_at[gte]` and `updated_at[lte]` together is a `422` on all five endpoints, so
`start_time_option`/`end_time_option` cannot be used — the window goes out as a single
`updated_at[date_range]=<start>~<end>` parameter per slice. `alerts`, `actions` and `follow-ups` take
exact timestamps (half-open `[start, end)` at millisecond precision) with a `PT5M`
`lookback_window`, because the vendor documents that those rows can commit out of timestamp order.
`incidents` and `escalations` match `date_range` by date, both ends inclusive, so their templates
format the bounds as `%Y-%m-%d`. The slice size is `step: {{ config.get('time_window') or 'P30D' }}`;
`cursor_granularity` is `PT0.000001S` because the CDK requires it whenever `step` is set.
`time_window` only accepts whole days (`^P[1-9][0-9]*D$`): `incidents` and `escalations` filter by
date, so a sub-day window would re-request the same day, and `PT1H` from the 2020 default is about
59,000 requests per stream. The overlap re-reads are de-duplicated by primary key when the
destination sync mode is Append + Deduped (with plain Append they are kept).

Record timestamps come back as `%Y-%m-%dT%H:%M:%S.%fZ`; older reports (airbytehq/alpha-beta-issues issues
1769 and 2926) show `%Y-%m-%dT%H:%M:%SZ` as well, so both are listed in `cursor_datetime_formats`.

On `actions` and `follow-ups`, an `incident_mode` partition that has never returned a record keeps
its cursor at `start_date`, so it re-scans every window on each incremental sync (about 83 requests
per empty mode per stream at `P30D` from 2020). If that traffic matters on a real account, tune
`time_window` or `start_date`.

**The cursor window applies to full-refresh syncs too.** A declarative stream with a
`DatetimeBasedCursor` sends the `updated_at` window whatever the sync mode, so the default
`start_date` has to predate all incident.io data. It is `2020-01-01`. A regression run
with a two-year default lost every 2023 record on an existing full-refresh connection; do not make the
default relative to "now".

## Page sizes

Each paginated stream uses the largest `page_size` the API serves (`incidents` 250,
`incident_updates` 250, `users` 10000, `alerts` 50, `alert_routes` 50, `incident_alerts` 50,
`escalations` 50, `escalation_paths` 25, `actions` and `follow-ups` 250, `catalog_entries` 250,
`custom_field_options` 250).
For `incidents` the OpenAPI spec allows 500, but the API caps it at 250: a request for 500 comes back
with `pagination_meta.page_size: 250`. One exception: `schedules` stays at 100 because the vendor
documents that `next_shifts` is only
returned when `page_size` is 25 or lower, and the connector does not emit `next_shifts` today. Lower it
to 25 if that field is ever added to the schema.

## Child-stream request cost

`incident_attachments` sends one request per incident. As a full-refresh child, it re-reads the
windowed `incidents` parent on every sync; the parent endpoint is limited to 60 requests per minute.
A 2,000-incident account therefore needs about 2,000 attachment requests plus the `incidents` read.
`incident_attachments` ignores 404 because an incident can be deleted after the parent read and
before its attachment partition runs. A missing incident returns HTTP 404 with error code
`resource_not_found` (confirmed live with a made-up incident ID), so a 404 here means a deleted or
unknown incident and nothing else. If a filter is added to `base_error_handler`, add a corresponding
`$ref` to the `incident_attachments` handler.

`incident_attachments` uses the windowed `incidents` stream as its parent, so a later `start_date`
also excludes attachments of incidents last updated before it. This is intentional: child streams
follow their parent's scope, and an unfiltered second `incidents` read would cost every sync.

`catalog_entries` sends one request per catalog type for each page of up to 250 entries.
`custom_field_options` sends one request per custom field, with additional requests when a field has
more than 250 options.

## Concurrency

`default_concurrency` reads `{{ config.get('num_workers') or 4 }}` — `num_workers` in the spec
(default 4, range 1-10, `max_concurrency` 10) sets how many streams and partitions are read in
parallel. Every worker shares the same `api_budget`, so raising it never exceeds the rate limit.

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
`((response.get('errors') or [{}])[0].get('message') or ...)[:300]`: the `or` matters, an empty `errors` list
would otherwise raise inside the error handler and turn a clear configuration error into a generic one.
The vendor message is cut to 300 characters so an oversized error body stays a readable message.

## `users` includes deactivated accounts

`users` sends `include_inactive=true` so deactivated or not-yet-active users are present, with the
vendor's `is_active` flag declared in the schema. Without it, a user who leaves the organisation
disappears from the stream.
