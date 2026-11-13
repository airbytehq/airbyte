> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-datadog: Unique Connector Behaviors

`CONTRIBUTING.md` summarizes the same behaviors for people. Keep the two files in step: a change to one of them is a change to the other.

Vendor facts below come from Datadog's OpenAPI specs at commit `068d9b5` of `DataDog/datadog-api-client-python` ([v1](https://github.com/DataDog/datadog-api-client-python/blob/068d9b5b97ed42a375bdba4d57868e8d9010b7c1/.generator/schemas/v1/openapi.yaml), [v2](https://raw.githubusercontent.com/DataDog/datadog-api-client-python/068d9b5b97ed42a375bdba4d57868e8d9010b7c1/.generator/schemas/v2/openapi.yaml)), named by operation, or were read live against a small test account on the date given.

## 1. Two Keys, One Permission per Stream, No OAuth

Every request carries an API key (`DD-API-KEY`) and an application key (`DD-APPLICATION-KEY`), both set once on `definitions.base_requester`. The connector has no OAuth flow because Datadog does not offer one to it: "OAuth is available only to approved Technology Partners developing official Datadog integrations. Standalone OAuth clients are not supported." ([Create an API-based integration](https://docs.datadoghq.com/extend/integrations/api_integration/)).

An application key can be scoped: "Scoped application keys are granted only the scopes specified by the user" ([API and application keys](https://docs.datadoghq.com/account_management/api-app-keys/)). A key can therefore read some streams and get a 403 on others. Each stream declares the permission its endpoint needs in `$parameters.required_permission`, taken from the `x-permission` of its operation, and the 403 message names it (section 5).

| Stream | Operation | Permission |
| --- | --- | --- |
| `audit_logs` | `ListAuditLogs` | `audit_logs_read` |
| `dashboards` | `ListDashboards` | `dashboards_read` |
| `downtimes` | `ListDowntimes` (v1) | `monitors_read` |
| `incidents` | `ListIncidents` | `incident_read` |
| `logs` | `ListLogsGet` | `logs_read_data` |
| `metrics` | `ListTagConfigurations` | `metrics_read` |
| `monitors` | `ListMonitors` | `monitors_read` |
| `service_level_objectives` | `ListSLOs` | `slos_read` |
| `synthetic_tests` | `ListTests` | `synthetics_read` |
| `users` | `ListUsers` | `user_access_read` |
| `incident_teams` | none: `GET /api/v2/teams` is no longer in the spec | none declared |

**Why this matters:** The connection check reads `dashboards` only, so a scoped key can pass the check and still fail on another stream. A new stream must declare `required_permission`, or its 403 message can only say "a permission that this stream requires".

## 2. Paging Differs per Endpoint, and `monitors` Has None

Each paginated stream sends the largest page size the vendor documents, or the documented default where the spec states no maximum.

| Stream | Size sent | What the vendor states | Next page |
| --- | --- | --- | --- |
| `audit_logs` | `page[limit]=1000` | default 10, maximum 1000 (`ListAuditLogs`) | `page[cursor]` from `meta.page.after` |
| `logs` | `page[limit]=5000` | default 10, maximum 5000 (`ListLogsGet`); 5001 is a 400 "Limit can't be more than 5000" (live, 2026-11-12) | `page[cursor]` from `meta.page.after` |
| `incidents` | `page[size]=100` | default 10, "The maximum allowed value is 100" (`ListIncidents`) | `page[offset]`, counted on the records read |
| `dashboards` | `count=100` | default 100, no maximum stated (`ListDashboards`) | `start`, counted on the records read |
| `service_level_objectives` | `limit=1000` | default 1000, no maximum stated (`ListSLOs`) | `offset`, counted on the records read |
| `synthetic_tests` | `page_size=100` | default 100, no maximum stated; `page_number` "Starts at zero" (`ListTests`) | `page_number` |
| `metrics` | `page[size]=10000` | default and maximum 10000 (`ListTagConfigurations`); 10001 is a 400 (live, 2026-11-12) | `page[cursor]` from `meta.pagination.next_cursor` |
| `users` | `page[size]=100` | default 10, "The maximum allowed value is 100" (`ListUsers`) | `page[number]` |
| `monitors` | none | `page`: "If this argument is not specified, the request returns all monitors without pagination." (`ListMonitors`) | none |
| `downtimes` | none | the deprecated v1 list takes no paging parameter (`ListDowntimes`) | none |

`incidents` pages by a counted offset and ignores `meta.pagination.next_offset`. When nothing is left, `next_offset` equals the offset that was sent (live, 2026-11-13: offset 5 on an empty list answers `next_offset: 5`), so a paginator that follows it repeats the last request without end. The three cursor streams (`audit_logs`, `logs`, `metrics`) stop on a missing or null cursor, on a null `meta`, and on an empty page.

The first request is the one Datadog's own client sends ([datadog-api-client-python](https://github.com/DataDog/datadog-api-client-python)): the size alone for `dashboards`, `incidents` and `service_level_objectives`, and the size with `page_number=0` for `synthetic_tests`.

`metrics` also sends `window[seconds]=5184000`. The window is "Only return metrics that have been actively reporting in this window", one hour by default and 60 days at most, so the stream lists the metrics of the last 60 days. `page[size]` must always be sent: without it "the response is not paginated and is capped at 250,000 metrics by default, with no indication when results are left out".

**Why this matters:** A larger size is a 400 on `logs` and `metrics`. Adding `page` to `monitors` switches that endpoint to pages of 100. Following `next_offset` on `incidents` hangs the sync as soon as an account holds an incident.

## 3. `logs` and `audit_logs` Send Microsecond Bounds Because the End Bound Is Exclusive

Both streams share one `DatetimeBasedCursor` (`definitions.timestamp_cursor`) on `sync_date`, a copy of `attributes.timestamp` made by `definitions.sync_date_from_timestamp`. They are the only incremental streams: `ListLogsGet` and `ListAuditLogs` are the only list operations the connector calls that take a time bound (`filter[from]`, `filter[to]`). The window applies to full refresh syncs as well.

Datadog reads `filter[from]` as inclusive and `filter[to]` as exclusive, at millisecond precision. The spec only says "Minimum timestamp" and "Maximum timestamp". Read live on 2026-11-13 on both endpoints: a `filter[to]` equal to a record's timestamp does not return the record, one millisecond later does; a `filter[from]` equal to the timestamp returns it, one millisecond later does not.

The range is cut into monthly windows (`step: P1M`), and each window ends one `cursor_granularity` before the next one starts. The cursor writes its bounds as `%Y-%m-%dT%H:%M:%S.%fZ` with a granularity of one microsecond, so two windows meet at `...T23:59:59.999999Z` and `...T00:00:00.000000Z`. Record timestamps have millisecond precision, so no record falls between them. Both endpoints accept six fractional digits (live, 2026-11-13).

Two other settings look equivalent and are not:

- Second-precision bounds with a step of one second (`...T23:59:59Z`, then `...T00:00:00Z`) lose every record of the last second of each window, because the end bound is exclusive.
- Second-precision bounds with the microsecond step, which the connector had before 2.1.0, never advance the cursor. Adjacent windows look one second apart, the CDK cannot merge them, and the saved state stays in the first window, so every sync reads the whole range again.

The saved state is the timestamp of the newest record, for example `{"sync_date": "2026-11-12T21:01:40.305000Z"}`. `cursor_datetime_formats` lists both the microsecond format and `%Y-%m-%dT%H:%M:%SZ`, so a state saved before 2.1.0 is still read, and 2.0.25 reads a state saved by 2.1.0.

`lookback_window` is `P1D`: every sync starts one day before the saved state. Datadog drops a log whose timestamp is more than 18 hours in the past when it arrives ([log pipelines](https://docs.datadoghq.com/logs/log_configuration/pipelines/), [logs troubleshooting](https://docs.datadoghq.com/logs/troubleshooting/)), so a late log cannot be more than 18 hours behind and one day covers it. With an empty `end_date` the window ends at the time of the sync, cut to the second; with an empty `start_date` it starts 30 days before the sync.

`logs` sends the `query` config field as `filter[query]`. `audit_logs` does not: the field holds a log search, and `ListAuditLogs` takes "Search query following Audit Logs syntax".

**Why this matters:** A change to `datetime_format`, `cursor_granularity` or `cursor_datetime_formats` changes which records are read at the seam of two windows and whether a saved state still parses. The state in `integration_tests/abnormal_state.json` must be in the format the cursor writes, or the standard tests fail.

## 4. Deleted Dashboards and SLOs Come From a Second Request

Datadog returns deleted records only on request. `ListDashboards` takes `filter[deleted]`: "When `true`, this query returns only deleted custom-created or cloned dashboards." `ListSLOs` takes `is_deleted`: "Whether to return only deleted service level objective objects."

`dashboards` and `service_level_objectives` each have a `ListPartitionRouter` with the values `false` and `true`, so each stream runs its paginated read twice, and an `AddFields` transformation sets a boolean `deleted` from the partition that returned the record. The vendor's list items (`DashboardSummaryDefinition`, `ServiceLevelObjective`) document no deletion field, so the request is the only thing that tells a deleted record from an active one. The primary key stays `id`, because a record comes back in one partition only.

**Why this matters:** `deleted` is set by the connector, not by Datadog. Removing the router drops deleted records without an error. The deleted side is proven by mock tests only: the test account held no deleted dashboard or SLO on 2026-11-13.

## 5. Error Map

Every stream uses `definitions.error_handler`: a `DefaultErrorHandler` with `max_retries: 5` that waits for `X-RateLimit-Reset` (the seconds until the limit resets) and otherwise backs off exponentially with factor 5. Error bodies are `{"errors": [string]}` (`APIErrorResponse`).

| Status | Stream | Cause | Action | Message |
| --- | --- | --- | --- | --- |
| 403 whose `errors` hold "Failed permission authorization checks" | all | the application key lacks the permission of the endpoint (live, 2026-11-13) | FAIL, `config_error` | "The Application Key lacks the `<permission>` permission: `<Datadog's text>`. Grant `<permission>` to the Application Key in Datadog." |
| 401, any other 403 | all | 401: a key that is too short, not hexadecimal or empty, or an application key of 40 zeros. 403: a well-formed key that is wrong, or valid keys sent to another site (live, 2026-11-13) | FAIL, `config_error` | "Datadog rejected the API Key or the Application Key: `<Datadog's text>`. Check that both keys are complete and valid and belong to the selected Site." |
| 400 | `logs` | the log search query does not parse (live, 2026-11-13) | FAIL, `config_error` | "Datadog rejected the log search query: `<Datadog's text>`. Check the Query field." |
| 404 | `synthetic_tests` | "Synthetic Monitoring is not activated for the user." (`ListTests`) | FAIL, `config_error` | "Synthetic Monitoring is not active for this Datadog account. Deselect the synthetic_tests stream or activate Synthetic Monitoring in Datadog." |
| 410 | `metrics` | "An expired cursor returns `410 Gone`; restart from the first page without `page[cursor]`." (`ListTagConfigurations`) | FAIL, `transient_error` | "The page cursor of the Datadog metrics list is expired. The next sync reads the list from the first page." |
| 429 | all | rate limit | CDK default: retry, after the wait `X-RateLimit-Reset` gives | |
| 408, 5xx | all | transient | CDK default: retry | |
| other 4xx | all | | CDK default: fail | the CDK's text |

The missing-permission filter matches on a `predicate` over the response body and declares no `http_codes`. The CDK matches a filter on its codes or on its predicate or on `error_message_contains`, so a filter with a code and a text condition would take every 403. The CDK also asks every filter about every response, a successful page included, so the predicate reads only the top-level `errors` of the body. `error_message_contains` is not used: on a response that is a list it searches the fields of every record, and a monitor whose message quotes Datadog's text would fail its page. If rendering a predicate raises a `TypeError`, the CDK treats the filter as matched, so keep the guarded way the template reads the body.

The templates that read the body accept a body that is not JSON, a JSON body that is not an object, a body without `errors`, and an `errors` value that is not a list of strings. The messages cut Datadog's text at 300 characters.

`logs`, `metrics` and `synthetic_tests` have a handler of their own that lists the stream's filter first and then the two shared filters by `$ref`.

**Why this matters:** A `config_error` stops the retries and shows its message to the user, so each one must name a cause the user can fix. A filter added to `definitions.error_handler` has to be added to the three stream handlers as well. A retry of the `metrics` 410 cannot succeed: without its filter the CDK repeats the request five times and then fails with a system error.

## 6. Rate Limits Are per Endpoint and Read From Headers

Datadog publishes no table of limits: "The rate limits for endpoints vary and are included in the headers" ([rate limits](https://docs.datadoghq.com/api/latest/rate-limits/)). A successful response carries `X-RateLimit-Limit`, `X-RateLimit-Period`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` and `X-RateLimit-Name`, and no `Retry-After`.

| Endpoint | Limit | Period | `X-RateLimit-Name` | Read live |
| --- | --- | --- | --- | --- |
| `/api/v2/audit/events` | 100 | 60 s | `audit_logs_public_search_api` | 2026-11-13 |
| `/api/v1/dashboard` | 60 | 60 s | `get_custom_dashboards` | 2026-11-12 |
| `/api/v1/downtime` | 60 | 60 s | `get_all_downtimes` | 2026-11-12 |
| `/api/v2/incidents` | 100 | 60 s | `incidents_list` | 2026-11-12 |
| `/api/v2/logs/events` | 300 | 60 s | `logs_public_search_api` | 2026-11-12 |
| `/api/v2/metrics` | 50 | 10 s | `metrics_list_v2_api` | 2026-11-12 |
| `/api/v1/monitor` | 1000 | 10 s | `get_all_monitors` | 2026-11-12 |
| `/api/v1/slo` | 1000 | 10 s | `slo_get_all` | 2026-11-12 |
| `/api/v1/synthetics/tests` | 12000 | 60 s | `synthetics_get_all_tests` | 2026-11-12 |
| `/api/v2/users` | no rate-limit header | | | 2026-11-12 |

`api_budget` has one `MovingWindowCallRatePolicy` per row with a limit. The path patterns are anchored (`^/api/v1/slo$`), so a policy applies to the list endpoint its limit was read on and to nothing else. `ratelimit_remaining_header: X-RateLimit-Remaining` keeps the local count honest: when Datadog reports zero calls left, or answers 429, the CDK fills the local window and the next call waits for it. After a 429 the retry therefore waits the header's time and then what is left of the window.

`ratelimit_reset_header` is not declared on purpose. `X-RateLimit-Reset` is the "time in seconds until next reset", and the CDK reads a reset header as a point in time. With a reset header declared, a moving-window policy also stops syncing its count with the API.

`concurrency_level` reads the `num_workers` spec field (3 by default, from 2 to 10). All workers share the budget.

**Why this matters:** The limits were read on one small account and are not a contract, so `X-RateLimit-Remaining` matters more than the numbers. A stream on a new endpoint needs a policy of its own, read from that endpoint's headers. An unanchored pattern would put a neighbouring path under the wrong limit.

## 7. Schema Fields Declared From Observed Values

Most properties are typed from the vendor's schemas. These are in live records and not in the spec, so they are declared with the kind that was observed:

| Field | Declared as | Seen |
| --- | --- | --- |
| `monitors.creator.id` | integer | 2026-11-12 |
| `monitors.matching_downtimes[].active` | boolean | 2026-11-12 |
| `monitors.matching_downtimes[].monitor_id` | integer | 2026-11-12 |
| `monitors.matching_downtimes[].groups` | array, with no `items`: only an empty list was ever seen | 2026-11-12 |
| `users.attributes.allowed_login_methods` | array of strings | 2026-11-12 |
| `users.attributes.is_access_configurable_bot` | boolean | 2026-11-12 |
| `logs.attributes.source` | string | 2026-11-13; absent from the same records a day earlier |

`dashboards.is_read_only` has a history. Datadog deprecated it ([guide](https://docs.datadoghq.com/dashboards/guide/is-read-only-deprecation/)), and 2.0.0 removed it from the schema as a breaking change. The API still returns it, and `DashboardSummaryDefinition` still lists it as deprecated, so 2.1.0 declares it again.

Every schema keeps `additionalProperties: true`, so a field the schema lacks never fails a sync.

**Why this matters:** The types in the table rest on one account's records, not on a vendor reference. Before a release, compare each stream's properties with the vendor's schema for its list item, and read the test account for fields the spec does not list.

## 8. What Only the Mock Tests Prove

`unit_tests/pyproject.toml` pins `airbyte-cdk` to the exact version of the base image in `metadata.yaml`. The tests assert things the CDK decides, such as the one second it adds to a backoff wait, so bump the two together.

The unit tests have a 30-second timeout with `timeout_method = "thread"`. A paginator that never stops fails there. The thread method ends the whole run at once, without a summary; it was chosen because with the signal method a reader thread outlived the mock and called the real API.

No test waits for real. The retry tests replace `time.sleep` and run on `users`, the one endpoint without a budget policy: with `time.sleep` replaced, a 429 on a budgeted endpoint makes the budget's wait loop spin. `now_is()` in `unit_tests/conftest.py` sets the clock that the manifest's macros read and nothing else.

The standard tests read every discovered stream except those under `empty_streams` in `acceptance-test-config.yml`, and a unit test checks that each of those has a mock test file. As of 2026-11-13 the test account could not show these, so only mock tests cover them:

- a second page on any stream, and any record of `incidents`, `synthetic_tests` and `downtimes`;
- the deleted side of `dashboards` and `service_level_objectives`;
- a 429 and its wait, the `synthetic_tests` 404 and the `metrics` 410.

**Why this matters:** A green run of the standard tests says little about paging, deleted records and error handling on this account. A change there needs the mock tests, and where it matters a read against a larger account.

## 9. Left for the Next Major Release

These are known and deliberately untouched, because fixing them changes a key, a type or the list of streams:

- `incident_teams` calls `GET /api/v2/teams`, which answers 404 and is no longer in the spec, so the stream fails on every sync. Its paginator also looks for the next offset in the last record, so a page with records would fail after emitting them. A mock test records both.
- `downtimes` reads the deprecated v1 list ("This endpoint has been deprecated. Please use v2 endpoints."), which does not return downtimes created with the v2 API. The v2 list has another record shape and needs the `monitors_downtime` permission.
- `synthetic_tests` declares no primary key.
- Several timestamp fields of existing streams are declared as plain strings or numbers, without `format: date-time`. `sync_date` of `logs` and `audit_logs` is among them: a format added to a field that is already declared is a breaking change, and a unit test keeps it out.
- The spec fields `max_records_per_request` and `queries` are read by no stream.

**Why this matters:** Each of these is a breaking change for existing connections. Do not fold one into a minor release.
