> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-pipedrive: Unique Behaviors

## 1. HTTP Error Classification Lives on the Shared Base Requester

Every stream `$ref`s `definitions.base_requester`, which carries `definitions.base_error_handler` (a `DefaultErrorHandler`). Pipedrive returns a JSON envelope `{"success": false, "error": "...", "errorCode": N}` for most failures; the filters interpolate `response.get('error')` into the user-facing message so the vendor text is preserved. `HttpResponseFilter` falls back to `{}` when the body is not JSON, so messages still render for HTML bodies.

| Status | Action | Failure type | Meaning / message intent |
|---|---|---|---|
| 401 | FAIL | `config_error` | API token invalid, revoked, or API access disabled for the user. Message tells the user where to copy a new token. |
| 402 | FAIL | `config_error` | Company account inactive (trial expired / billing missing). |
| 403 | FAIL | `config_error` | Token owner lacks permission, plan does not include the data, **or** Cloudflare blocked the token after repeated rate-limit abuse (HTML body, no `error` key). |
| 410 | FAIL | `system_error` | Endpoint permanently removed by Pipedrive. |
| 429 | RATE_LIMITED | transient | Burst or daily budget exceeded; retried with backoff (see below). |
| 500, 502, 503, 504 | RETRY | transient | Temporary server error. |
| other 4xx/5xx | CDK default mapping | — | e.g. 404 on a top-level stream fails as `system_error`. |

Backoff for RETRY / RATE_LIMITED (`max_retries: 10`): `WaitTimeFromHeader` on `x-ratelimit-reset` (interpreted as seconds, capped at `max_waiting_time_in_seconds: 300`), then `ExponentialBackoffStrategy` (`factor: 5`) when the header is absent.

**Why this matters:** Before these handlers existed every non-2xx response used the CDK default mapping, which discarded Pipedrive's `error` text and treated 402/410 as retryable. Keep the filters on `base_requester` so new endpoints (including a future v2 migration) inherit them; do not add per-stream copies unless the stream needs different behavior.

## 2. Substreams Skip a Missing or Inaccessible Parent Instead of Failing the Sync

`deal_products` (`GET v1/deals/{deal_id}/products`) and `mail` (`GET v1/mailbox/mailThreads/{id}/mailMessages`) issue one request per parent record. Their requesters override `error_handler` with a `CompositeErrorHandler`:

1. `definitions.substream_missing_parent_error_handler` — IGNORE 403, 404, 410 (parent deleted/merged after the parent stream was read, or not visible to the token owner). A warning with Pipedrive's `error` text is logged and the remaining parents continue.
2. `definitions.base_error_handler` — everything else (401, 402, 429, 5xx) falls through to the shared behavior above.

**Why this matters:** A single deal the token owner cannot read used to abort the whole `deal_products` sync with a 403. Do not extend the IGNORE list to top-level streams; a 403/404 there indicates a real configuration or API problem.

## 3. Rate Limits: Burst vs Daily Budget

Pipedrive enforces two independent limits per API token ([docs](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting)):

- **Burst:** rolling 2-second window, 20/40/100/120 requests per 2s depending on plan (Lite/Growth/Premium/Ultimate). A 429 here carries `x-ratelimit-reset` (observed value `2`) and `Retry-After`; the handler waits and succeeds on retry.
- **Daily token budget:** 30,000 x plan multiplier x seats per day. When exhausted, *every* request returns 429 until midnight (Pipedrive server time). Backoff cannot fix this; after `max_retries` the sync fails and the 429 message explains the daily budget so the user can reduce frequency or upgrade. Proactive prevention via an `api_budget` is tracked separately and is intentionally not implemented here.

**Why this matters:** A test or triage that only looks at "429 => retry" will miss that daily-budget 429s are unrecoverable within a sync.

## 4. Null Payload Tombstones

Several endpoints (e.g. `v1/recents`) return `{"success": true, "data": null}` when there are no records. The custom `NullCheckedDpathExtractor` in `components.py` treats a null `data` as an empty list instead of raising. This is the connector's only custom Python component; error handling is entirely declarative.

## Testing

- `unit_tests/` contains mock-server tests (`airbyte_cdk.test.mock_http.HttpMocker`) for each error filter and the substream IGNORE behavior. Run with `cd unit_tests && poetry install && poetry run pytest`.
- `integration_tests/invalid_token_config.json` exercises the 401 path of `check`.
- Live credentials are in GSM (`SECRET_SOURCE-PIPEDRIVE__CREDS`); fetch with `uvx 'airbyte-cdk[dev]' secrets fetch`.
