> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-incident-io: Unique Behaviors

`CONTRIBUTING.md` explains the same behaviours for people. Keep the two files in step: a change to one of them is a change to the other.

## 1. API-Key-Only Authentication, With Permission Errors That Name the Scope

incident.io authenticates with a bearer API key only (`components.securitySchemes.BearerAuth` in https://api.incident.io/v1/openapiV3.json). There is no OAuth flow. Keys are created under Settings > API keys and carry per-resource view permissions (`incidents.view`, `workflows.view`, …), so a key can read some streams and get HTTP 403 on others.

The 403 response filter in `base_error_handler` interpolates the vendor's message into a `config_error`: `errors[0].message` names the missing permission. The template reads `((response.get('errors') or [{}])[0].get('message') or '…')[:300]`; the `or` guards an empty `errors` list, which would otherwise raise inside the handler and turn a clear configuration error into a generic one. The 300-character cap keeps an oversized body readable.

**Why this matters:** A 403 is a per-stream configuration problem, never a bug. The user fixes it by granting the permission or deselecting the stream; the connector must not retry it. The user docs list the permission each stream needs.

## 2. `/v3` Endpoints Default to Two Incident Modes, So Three Streams Fan Out Over Five

`/v3/actions` and `/v3/follow_ups` return records from `standard` and `retrospective` incidents only unless `incident_mode` is set. The deprecated `/v2` endpoints returned every mode. To keep parity, both streams use a `ListPartitionRouter` over `standard`, `retrospective`, `test`, `tutorial`, `stream`, one request series per mode. `incidents` sends the same five values as repeated `mode[one_of]` parameters, and all eight `status_category[one_of]` values, because `/v2/incidents` otherwise omits `declined`, `canceled` and `merged`.

A new vendor mode goes in three places in `manifest.yaml` (the two routers and the `incidents` requester) and in `_MODES` in `unit_tests/test_v3_streams.py`; a new status category goes in the `incidents` requester and `_STATUS_CATEGORIES`. Records of an unlisted mode silently stop syncing.

**Why this matters:** The partitions never overlap (each record has exactly one mode), so this is a request-count cost, not a dedup problem: five paginated passes per stream per sync, trivial against the 1,200/min limit. Dropping the router would silently lose records on real accounts (91 of 224 actions on one internal account).

## 3. Incremental Sync Uses a Single `updated_at[date_range]` Window Per Slice

`incidents`, `alerts`, `escalations`, `actions` and `follow-ups` are incremental on `updated_at`. Sending `updated_at[gte]` and `updated_at[lte]` together is a 422 on every endpoint, so the cursor cannot use `start_time_option`/`end_time_option`; each slice goes out as one `updated_at[date_range]=<start>~<end>` parameter. `alerts`, `actions` and `follow-ups` take millisecond timestamps (half-open, `PT5M` lookback because the vendor documents out-of-order commits); `incidents` and `escalations` match by date, both ends inclusive, so their templates format `%Y-%m-%d`. The vendor accepts `%Y-%m-%dT%H:%M:%S.%fZ` and `%Y-%m-%dT%H:%M:%SZ`, both listed in `cursor_datetime_formats`.

The slice size is `step: {{ config.get('time_window') or 'P30D' }}`, whole days only (`^P[1-9][0-9]*D$`): `incidents` and `escalations` filter by date, so a sub-day window re-requests the same day. The window applies to full-refresh syncs too, which is why the default `start_date` is `2020-01-01`: a relative default (two years) lost every 2023 record on an existing full-refresh connection. An `incident_mode` partition that has never returned a record keeps its cursor at `start_date` and re-scans every window on each sync (about 83 requests per empty mode per stream at `P30D`).

**Why this matters:** Changing the window shape, the date formats or the default start date changes which rows existing connections receive. Prove any change with a regression run against a real connection, not the three-record sandbox.

## 4. Two Rate Policies, Because `/v2/incidents` Is Capped at 60 Requests per Minute

The key allows 1,200 requests per minute, but `GET /v2/incidents` returns `x-ratelimit-limit: 60, 1200;window=60, 60;window=60` (checked live 2026-10-07). `api_budget` therefore has two `MovingWindowCallRatePolicy` entries matched in order: 60/min for `^/v2/incidents$`, 1,200/min for everything else. `ratelimit_remaining_header: x-ratelimit-remaining` drains the local bucket when the API reports zero. `x-ratelimit-reset` is not declared on purpose: with a moving-window policy the CDK only syncs the bucket when no reset header is present. A 429 is `RATE_LIMITED` and waits for `retry-after` (up to 600 seconds).

`concurrency_level.default_concurrency` is `{{ config.get('num_workers') or 4 }}` with `max_concurrency: 10`. Every worker shares the budget, so raising `num_workers` never exceeds the limits.

**Why this matters:** A single 1,200/min budget would let a large first sync of `incidents` burn its five retries on consecutive 429s. The `incidents` cap also bounds every stream that reads `incidents` as a parent (section 6).

## 5. Error-Handler Map

`base_error_handler` (`DefaultErrorHandler`, `max_retries: 5`, `WaitTimeFromHeader: retry-after` then `ExponentialBackoffStrategy` factor 5):

| Status | Action | Failure type | Message |
| --- | --- | --- | --- |
| 401 | FAIL | `config_error` | key invalid or revoked; create a new key |
| 403 | FAIL | `config_error` | vendor message naming the missing permission (section 1) |
| 429 | RATE_LIMITED | | waits for `retry-after` |
| 408, 500, 502, 503, 504 | RETRY | | transient |
| 400, 404, 405, 406, 409, 412, 413, 422 | FAIL | `system_error` | vendor message, capped at 300 characters |

`incident_attachments` has its own `DefaultErrorHandler`: a 404 `IGNORE` filter first, then `$ref`s to the base filters. An incident can be deleted between the parent read and its attachment partition; a missing incident returns 404 with error code `resource_not_found` (confirmed live), so 404 here means a deleted or unknown incident and nothing else. If a filter is added to `base_error_handler`, add the matching `$ref` to the `incident_attachments` handler.

**Why this matters:** `config_error` is reserved for failures the user can fix (key, permissions). Everything else that is not retryable is a `system_error` carrying the vendor's text, so the platform's failure classification stays honest.

## 6. Three Child Streams Pay One Request per Parent Record

- `incident_attachments` reads `/v1/incident_attachments?incident_id=…` once per incident from the windowed `incidents` parent. As a full-refresh child it re-reads the parent on every sync at 60 requests per minute, then sends one request per incident. A 2,000-incident account costs about 2,000 attachment requests plus the parent read. A later `start_date` also excludes attachments of older incidents, by design.
- `catalog_entries` reads one page series of up to 250 entries per catalog type from `catalog_types`.
- `custom_field_options` reads one request per custom field from `custom_fields`, more when a field has over 250 options.

Page sizes are the largest each endpoint serves: 250 for `incidents`, `incident_updates`, `actions`, `follow-ups`, `catalog_entries`, `custom_field_options`; 50 for `alerts`, `alert_routes`, `incident_alerts`, `escalations`; 25 for `escalation_paths`; 10,000 for `users`. The spec allows 500 on `incidents` but the API caps it at 250. `alert_routes` returns a `pagination_meta.after` cursor on its last page, so each sync makes one extra empty request. `schedules` stays at 100 because `next_shifts` is only returned at `page_size` 25 or lower, and the connector does not emit `next_shifts`; lower the page size to 25 before declaring that field.

**Why this matters:** Request volume, not record volume, is what limits a sync on this API. Adding a child stream or lowering a page size multiplies requests against the budgets in section 4.

## 7. Schemas Follow the List Endpoint's Documented Object

Every declared property comes from the object the stream's **list** endpoint returns in the vendor OpenAPI (https://api.incident.io/v1/openapiV3.json), not the by-id object. The two differ: `GET /v2/workflows` returns `WorkflowSlimV2`, which has no `form_fields`; both `alert_routes` list endpoints return `id`, `name`, `enabled` only. All schemas keep `additionalProperties: true`, so an undeclared field never fails a sync; it shows up in Datadog as `airbyte.schemas_unexpected_fields` instead, which is the certification signal (S-6). Declared types are decided by the vendor reference, never by observed values alone, and no vendor enum is declared as an `enum`, so a new vendor value cannot fail validation. Date-time strings are declared with `format: date-time` and `airbyte_type: timestamp_with_timezone` (57 fields since 1.0.0).

Deliberate omissions: `alert_sources.secret_token` (removed before records are emitted; it is a credential), `schedules.next_shifts` (section 6). To check the declared set against the spec, resolve each stream's list path in `paths`, follow the 200 response to the records array's item schema, and diff its `properties` against `schemas.<stream>.properties` in `manifest.yaml`.

**Why this matters:** A field the vendor documents but the schema omits is invisible until a customer's data carries it, at which point every sync reports it until a patch release declares it (0.4.2, 1.0.1 and 1.0.2 each did this for fields that had been documented all along). Diff against the spec before a release instead of waiting for Datadog.

## 8. `users` Includes Deactivated Accounts

`users` sends `include_inactive=true` and declares the vendor's `is_active` flag. Without it, a user who leaves the organisation disappears from the stream, which breaks joins from `incidents` and `escalations` to the people involved.

## 9. 1.0.0 Was a Breaking Release With `deadlineAction: disable`

1.0.0 typed 49 more timestamp fields, moved `catalog_types` and `alert_routes` to `/v3` (`semantic_type` removed, four fields added on `catalog_types`), and started sending all five incident modes on `incidents`. Auto-upgrading would silently have added test, tutorial and stream incidents to existing connections, so `releases.breakingChanges."1.0.0"` uses `deadlineAction: disable` with an upgrade deadline of 2026-11-09 and a `scopedImpact` of 14 streams. The migration guide is `docs/integrations/sources/incident-io-migrations.md`.

**Why this matters:** The `/v2/actions` and `/v2/follow_ups` endpoints are removed on 2026-12-31 (airbytehq/oncall#13520); connections still on 0.1.x, which read those endpoints, stop working then regardless of the deadline. Any further change to cursor shape, partition keys or state serialization is also breaking; declaring optional fields or bumping the base image within the same major is not.
