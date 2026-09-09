# source-pipedrive: Unique Connector Behaviors

## 1. Incremental Streams Read From the Recents Endpoint, Not the Entity Endpoints

The ten incremental streams (`activities`, `deals`, `files`, `filters`, `notes`, `persons`, `pipelines`, `products`, `stages`, `users`) do not call their entity endpoints (`/deals`, `/persons`, and so on). They all call [`GET /v1/recents`](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with an `items=<type>` parameter and a `since_timestamp` derived from the `DatetimeBasedCursor`. The start date is reformatted from the spec's `YYYY-MM-DDTHH:MM:SSZ` to the `YYYY-MM-DD HH:MM:SS` format that `/recents` requires. Every one of these streams uses `update_time` as the cursor except `users`, whose records expose `modified` instead, and `users` also unwraps one extra `data` level (`data.*.data.*`) because `/recents?items=user` nests an array under each item.

**Why this matters:** `/recents` returns anything modified since the timestamp, so these streams see edits to old records but never see records that were created before the start date and not touched since. Switching a stream to its entity endpoint changes the record scope (and would need a different cursor and pagination), so that is a data-scope change, not a refactor. Since 2024-12-01 Pipedrive caps `since_timestamp` on `/recents` at one month of history, so these streams never backfill records last modified earlier than that; the API v2 migration ([airbyte-internal-issues#17204](https://github.com/airbytehq/airbyte-internal-issues/issues/17204)) removes the cap. The remaining sixteen streams are full refresh and ignore `replication_start_date` entirely, except `deal_products`, whose parent is the recents-fed `deals` stream.

## 2. Null-Payload Records From Recents Are Kept as Tombstones

`/recents` wraps each item as `{"item": "deal", "id": 123, "data": {...}}`, and `data` can be `null`. The custom `NullCheckedDpathExtractor` in `components.py` returns `record["data"]` when it is present and otherwise returns the wrapper object itself, so a `null` payload becomes a record containing only `item` and `id`. Airbyte added this in [#31147](https://github.com/airbytehq/airbyte/pull/31147) after syncs crashed on `null` payloads.

**Why this matters:** Downstream tables for the incremental streams can contain sparse rows with just `id` and `item`. Do not add a `RecordFilter` to drop them without confirming users are not relying on them, and do not replace the extractor with a plain `DpathExtractor` on `data.*.data` (that would fail again on `null`). Issue [airbyte-internal-issues#17204](https://github.com/airbytehq/airbyte-internal-issues/issues/17204) owns moving these streams to API v2, which will remove the extractor; until then this behavior is intentional.

## 3. Custom Fields Arrive as Hash Keys Outside the Declared Schema

Pipedrive returns custom fields on deals, persons, organizations, products, and activities as 40-character hash keys (for example `dcf558aac1ae4e8c4f849ba5e668430d8df9be12`) alongside the built-in properties. The stream schemas set `additionalProperties: true` ([#31151](https://github.com/airbytehq/airbyte/pull/31151)) so those keys pass through, and the `*_fields` streams (`deal_fields`, `person_fields`, `organization_fields`, `product_fields`, `activity_fields`) expose the mapping from hash key to label and type.

**Why this matters:** Turning on `autoImportSchema`, tightening `additionalProperties`, or adding schema normalization would silently drop every custom field. Because the keys differ per Pipedrive account, they can never be listed in the static schema.

## 4. Authentication Is a Query Parameter, Not an Authenticator

There is no `authenticator` in the manifest. Every stream injects `api_token: "{{ config['api_token'] }}"` into `request_parameters`, which is how Pipedrive's [API token auth](https://pipedrive.readme.io/docs/core-api-concepts-authentication) works. The token belongs to a single user, so all streams are scoped to that user's visibility and permission set.

**Why this matters:** The token is part of the URL, so it appears in request logs and in any debug output that prints URLs. It also means `check` succeeding does not imply the token can see company-wide data. Issue [airbyte-internal-issues#17201](https://github.com/airbytehq/airbyte-internal-issues/issues/17201) owns adding OAuth and moving auth to a header; do not document or add OAuth ahead of that work.

## 5. Mail Streams Are Scoped to One User's Mailbox and Fan Out per Folder and Thread

`mailThreads` calls [`GET /v1/mailbox/mailThreads`](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreads) once per folder using a `ListPartitionRouter` over `inbox`, `drafts`, `sent`, and `archive`. `mail` is a substream that calls [`GET /v1/mailbox/mailThreads/{id}/mailMessages`](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreadMessages) for every thread `mailThreads` returns. Pipedrive's mailbox endpoints only return the mailbox of the token's user.

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

`deal_products` and `mail` issue one request per parent record and override `error_handler` with a `CompositeErrorHandler`: `definitions.substream_missing_parent_error_handler` IGNOREs 403, 404 and 410 for a single parent (deleted or merged after the parent stream was read, or not visible to the token owner) with an INFO log line, then falls through to the shared handler. A parent-list 403 still fails the sync; a token-wide 403 on the child endpoint leaves the child stream silently empty.

Pipedrive enforces two independent limits per API token ([docs](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)): a rolling 2-second burst window (20/40/100/120 requests by plan) that recovers after a short wait, and a daily token budget (30,000 tokens x plan multiplier x seats) that, once exhausted, returns 429 on every request until midnight in Pipedrive's server timezone. Backoff cannot fix the second case; the 429 message says so.

**Why this matters:** Keep the filters on `base_requester` so new endpoints (including the API v2 migration) inherit them; do not add per-stream copies. Do not extend the IGNORE list to top-level streams. Tests must not assert on retry log text, which comes from the CDK or the backoff library and changes between versions.

## 7. One Shared Request Budget and a Small Thread Pool

The manifest declares a top-level `api_budget` (`HTTPAPIBudget` with one `MovingWindowCallRatePolicy`: 20 requests per rolling 2 seconds) and a `concurrency_level` (`default_concurrency` from the optional `num_workers` config field, default 3, `max_concurrency` 10). The policy's `HttpRequestRegexMatcher` matches on the URL path (`^(/api)?/v[12]/`), not on the host, so it covers `https://api.pipedrive.com/v1/...`, `/api/v2/...` and the per-company hosts that OAuth uses. 20 per 2 seconds is the burst limit of Pipedrive's lowest plan ([docs](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)); the plan is not knowable from the config, so the floor is used. `x-ratelimit-reset` is deliberately not read: Pipedrive sends a relative number of seconds and the CDK parses that header as an epoch timestamp. `x-ratelimit-remaining` and a 429 only nudge the bucket when Pipedrive reports zero calls left; the moving window is the actual throttle.

**Why this matters:** Every stream shares the one budget, so more workers never exceed the burst limit and rarely make a sync faster. The daily token budget (30,000 tokens x plan multiplier x seats) is not modeled and remains the dominant limit for large accounts; see section 6 for how a 429 from an exhausted daily budget is reported. Do not add per-stream budgets or a second policy; tune the single `Rate` if the floor ever changes. Parent streams that the CDK caches (`deals`, `mailThreads`) share one HTTP session across partitions, so keep `max_concurrency` modest.

## 8. Deletes Are Not Replicated

No stream emits deletion markers or filters on a deleted flag. `/recents` reflects edits, not deletions, and the full refresh streams re-read the live collection. Issue [airbyte-internal-issues#17204](https://github.com/airbytehq/airbyte-internal-issues/issues/17204) owns the API v2 migration that may change how deleted records surface.

**Why this matters:** Destinations keep rows for records deleted in Pipedrive until the user clears the stream. Do not describe the tombstone rows from section 2 as deletions in user-facing docs; the relationship between `null` payloads and deletions has not been confirmed against the API.
