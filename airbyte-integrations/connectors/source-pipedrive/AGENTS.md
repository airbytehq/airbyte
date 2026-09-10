# source-pipedrive: Unique Connector Behaviors

## 1. Incremental Streams Use API v2 Entity Endpoints

The incremental core streams (`activities`, `deals`, `organizations`, `persons`, and `products`) call `api/v2/...` entity endpoints with cursor pagination and an inclusive `updated_since` filter. `notes` and `files` use `v1/...` list endpoints and filter records client-side by `update_time`. Pipelines, stages, filters, and users are full refresh. `deal_flow` remains a child stream of `deals`.

The shared base URL is `https://api.pipedrive.com/`, not `/api/`: v1 leads, lead labels, lead sources, goals, and mailbox endpoints are only available on the bare host. API v2 requests therefore include the `api/` path explicitly.

## 2. API v2 Records and Custom Fields

API v2 list responses contain records under `data` and the next cursor under `additional_data.next_cursor`. Core v2 records expose custom values under a nullable `custom_fields` object and may include `is_deleted`.

## 3. Custom Fields Are Nested Under `custom_fields`

Pipedrive returns custom fields on deals, persons, organizations, products, and activities as account-specific hash keys. API v2 records place those values under the nullable `custom_fields` object, and the schemas preserve them with `additionalProperties: true`. The `*_fields` streams expose the mapping from each hash key to its label and type; join on the `key` column when a readable field name is needed.

## 4. Authentication Is a Query Parameter, Not an Authenticator

There is no `authenticator` in the manifest. Every stream injects `api_token: "{{ config['api_token'] }}"` into `request_parameters`, which is how Pipedrive's [API token auth](https://pipedrive.readme.io/docs/core-api-concepts-authentication) works. The token belongs to a single user, so all streams are scoped to that user's visibility and permission set.

**Why this matters:** The token is part of the URL, so it appears in request logs and in any debug output that prints URLs. It also means `check` succeeding does not imply the token can see company-wide data. Issue [airbyte-internal-issues#17201](https://github.com/airbytehq/airbyte-internal-issues/issues/17201) owns adding OAuth and moving auth to a header; do not document or add OAuth ahead of that work.

## 5. Mail Streams Are Scoped to One User's Mailbox and Fan Out per Folder and Thread

`mailThreads` calls [`GET /v1/mailbox/mailThreads`](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreads) once per folder using a `ListPartitionRouter` over `inbox`, `drafts`, `sent`, and `archive`. `mail` is a substream that calls [`GET /v1/mailbox/mailThreads/{id}/mailMessages`](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreadMessages) for every thread `mailThreads` returns. These v1 mailbox endpoints are only available under the bare `https://api.pipedrive.com/` host. Pipedrive's mailbox endpoints only return the mailbox of the token's user.

**Why this matters:** The same thread can be emitted from more than one folder, so `mailThreads` can contain duplicate `id` values within a sync, and `mail` issues one request per thread, which dominates request volume on busy mailboxes. Neither stream can see other users' mail regardless of admin rights.

## 6. HTTP Errors Are Classified on the Shared Base Requester

Every stream `$ref`s `definitions.base_requester`, which carries `definitions.base_error_handler` (a `DefaultErrorHandler`). Pipedrive returns a JSON envelope `{"success": false, "error": "...", "errorCode": N}` for most failures; the filters interpolate `response.get('error')` into the user-facing message so the vendor text is preserved, and fall back to plain text when the body is not JSON (Cloudflare returns an HTML 403 after repeated rate-limit abuse).

| Status | Action | Failure type | Meaning |
|---|---|---|---|
| 401 | FAIL | `config_error` | API token invalid, revoked, or API access disabled for the user |
| 402 | FAIL | `config_error` | Company account inactive (trial expired or billing missing) |
| 403 | FAIL | `config_error` | Token owner lacks permission, the plan does not include the data, or Cloudflare blocked the token |
| 410 | FAIL | `system_error` | Endpoint permanently removed by Pipedrive |
| 429 | RATE_LIMITED | transient | Burst or daily budget exceeded; retried with backoff |
| 500, 502, 503, 504 | RETRY | transient | Temporary server error |
| other | CDK default mapping | | e.g. 404 on a top-level stream fails as `system_error` |

Backoff for RETRY and RATE_LIMITED (`max_retries: 10`): `WaitTimeFromHeader` on `x-ratelimit-reset` (Pipedrive reports a relative number of seconds; there is no `Retry-After`), then `ExponentialBackoffStrategy` with factor 5 when the header is absent. `max_waiting_time_in_seconds: 300` is a kill-switch, not a cap: if the header reports 300 s or more the stream stops with a transient error instead of waiting. Header-less retries are bounded by the CDK's 600 s `max_time`, so they get about seven attempts, not eleven.

`deal_products`, `deal_flow` and `mail` issue one request per parent record (`deal_installments` batches 100 deal ids per request through a `GroupingPartitionRouter`) and override `error_handler` with a `CompositeErrorHandler`: `definitions.substream_missing_parent_error_handler` IGNOREs 403, 404 and 410 for a single parent (deleted or merged after the parent stream was read, or not visible to the token owner) with an INFO log line, then falls through to the shared handler. A parent-list 403 still fails the sync; a token-wide 403 on the child endpoint leaves the child stream silently empty.

Pipedrive enforces two independent limits per API token ([docs](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)): a rolling 2-second burst window (20/40/100/120 requests by plan) that recovers after a short wait, and a daily token budget (30,000 tokens x plan multiplier x seats) that, once exhausted, returns 429 on every request until midnight in Pipedrive's server timezone. Backoff cannot fix the second case; the 429 message says so.

**Why this matters:** Keep the filters on `base_requester` so new endpoints (including the API v2 migration) inherit them. A per-stream `error_handler` must be a `CompositeErrorHandler` that lists the stream-specific IGNORE filter first and `$ref`s `base_error_handler` second: `$ref` merging is key-level, so a plain per-stream `DefaultErrorHandler` replaces the shared handler wholesale and loses every message, the 429 wait and `max_retries`. IGNORE on a top-level stream is allowed only for the plan or feature gating that Pipedrive reports for the whole endpoint, each with an INFO log line naming the feature: 402/403/404 on `projects` and `tasks` (Projects add-on), 402/403 on `deal_installments`, 403 on `permission_set_assignments`, 403/404/410 on `legacy_teams` (legacy Teams disabled or retired). Tests must not assert on retry log text, which comes from the CDK or the backoff library and changes between versions.

## 7. One Shared Request Budget and a Small Thread Pool

The manifest declares a top-level `api_budget` (`HTTPAPIBudget` with one `MovingWindowCallRatePolicy`: 20 requests per rolling 2 seconds) and a `concurrency_level` (`default_concurrency` from the optional `num_workers` config field, default 3, `max_concurrency` 10). The policy's `HttpRequestRegexMatcher` matches on the URL path (`^(/api)?/v[12]/`), not on the host, so it covers `https://api.pipedrive.com/v1/...`, `/api/v2/...` and the per-company hosts that OAuth uses. 20 per 2 seconds is the burst limit of Pipedrive's lowest plan ([docs](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)); the plan is not knowable from the config, so the floor is used. `x-ratelimit-reset` is deliberately not read: Pipedrive sends a relative number of seconds and the CDK parses that header as an epoch timestamp. `x-ratelimit-remaining` and a 429 only nudge the bucket when Pipedrive reports zero calls left; the moving window is the actual throttle.

**Why this matters:** Every stream shares the one budget, so more workers never exceed the burst limit and rarely make a sync faster. The daily token budget (30,000 tokens x plan multiplier x seats) is not modeled and remains the dominant limit for large accounts; see section 6 for how a 429 from an exhausted daily budget is reported. Do not add per-stream budgets or a second policy; tune the single `Rate` if the floor ever changes. Parent streams that the CDK caches (`deals`, `mailThreads`) share one HTTP session across partitions, so keep `max_concurrency` modest.

## 8. Deletes

The deals stream requests `status=open,won,lost,deleted`; deleted deals are emitted with `is_deleted: true` for up to 30 days after deletion. API v2 records include `is_deleted` where provided, and users may expose their deletion flag. Only deleted deals are enumerated as records; other streams may carry a vendor `is_deleted` flag, but deleted records are not enumerated.

Child streams tolerate missing or deleted parent records through their stream-specific `CompositeErrorHandler`, which ignores documented parent-level 403/404/410 responses before falling through to the shared base handler.
