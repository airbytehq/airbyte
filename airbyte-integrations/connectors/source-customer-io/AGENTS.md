# source-customer-io: Unique Connector Behaviors

## 1. The App API Is API-Key-Only

`definitions.base_requester` sends the App API key as a bearer token. That is the only scheme the three list endpoints accept: `listCampaigns`, `listCampaignActions` and `listNewsletters` declare `security: Bearer-Auth` in the [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) ([authentication](https://docs.customer.io/integrations/api/app/#authentication)). Customer.io's OAuth 2.0 flow exists only for its MCP server ([auth.md](https://docs.customer.io/auth.md)), and `sa_live_` service-account tokens work only on the transactional send endpoints (`components.securitySchemes.ServiceAccount-Auth` in the spec). The Region field selects `https://api.customer.io/v1` or `https://api-eu.customer.io/v1`.

**Why this matters:** There is no OAuth flow to add for these endpoints. App API keys are not Track API keys ([Track vs App keys](https://docs.customer.io/accounts/settings/managing-credentials/#track-api-keys-vs-app-api-keys)) and are shown only once ([App API keys](https://docs.customer.io/accounts/settings/managing-credentials/#app-api-keys)). Customer.io does not redirect App API requests to the other region, so a wrong Region fails with 401 like an invalid key ([data centers](https://docs.customer.io/accounts/settings/data-centers/#specifying-your-region-in-the-api)).

## 2. HTTP Errors Are Classified on the Shared Base Requester

Every requester, including the `campaigns` parent copy inside the `campaigns_actions` partition router, `$ref`s `definitions.base_requester`, which carries one `DefaultErrorHandler`. The `campaigns_actions` requester wraps it in a `CompositeErrorHandler` that first ignores 404.

| Status | Action | Failure type | Meaning |
| --- | --- | --- | --- |
| 401 | FAIL | `config_error` | Invalid key, a Track API key, the wrong Region, or an IP address outside the allowlist; the message names each fix |
| 403 | FAIL | `config_error` | Access denied; the message points to the IP allowlist |
| 429 | RATE_LIMITED | `transient_error` | Over the 10 requests per second limit; retried |
| 500, 502, 503, 504 | RETRY | `transient_error` | Temporary server error; retried |
| 404 on `listCampaignActions` | IGNORE | - | The automation was deleted after the automation list was read; its actions are skipped |
| 400 | FAIL (CDK default) | `system_error` | `listCampaignActions`: invalid campaign ID |
| Other | CDK default mapping | As mapped | For example 408 is retried and 405 fails; codes the CDK does not map are retried |

Retries wait for `Retry-After` (plus the one second the CDK adds) and fall back to `ExponentialBackoffStrategy` with factor 2 (4, 8, 16 s and so on) when the header is absent. They stop after `max_retries: 30` or the CDK's 600 s limit, whichever comes first. The CDK defaults live in `airbyte_cdk/sources/streams/http/error_handlers/default_error_mapping.py`.

The [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) documents 200 and 429 for [`listCampaigns`](https://docs.customer.io/integrations/api/app/tag/automations/listcampaigns/), 200, 400, 404 and 429 for [`listCampaignActions`](https://docs.customer.io/integrations/api/app/tag/automations/listcampaignactions/), and only 200 for [`listNewsletters`](https://docs.customer.io/integrations/api/app/tag/newsletters/listnewsletters/). A 429 carries `Retry-After` ([API rate limits](https://docs.customer.io/integrations/api/customerio-apis/#api-rate-limits)); the spec's header description adds that it is absent when a daily quota is hit, which is when the exponential backoff applies. `components.responses.Unauthorized` describes 401 as a missing or invalid API key.

**Why this matters:** Keep the filters on `base_requester` so every requester inherits them; `$ref` merging is key-level, so a per-stream `error_handler` replaces the shared one and loses the messages and the backoff. Customer.io does not document which status a blocked IP address gets ([IP allowlist](https://docs.customer.io/accounts/settings/managing-credentials/#restrict-api-access-by-ip-address)), so both messages mention the allowlist. In the `campaigns_actions` composite, the 404 handler repeats `max_retries: 30` because the composite reads `max_retries` from its first handler, and the shared handler stays last because the composite returns the last handler's FAIL, which keeps the 401 and 403 messages.

## 3. One Shared Request Budget and Three Workers

The manifest declares `concurrency_level` (`default_concurrency: 3`) and an `api_budget` with one `MovingWindowCallRatePolicy` of 10 requests per rolling second and `matchers: []`, so the policy covers every request. Most App API endpoints allow 10 requests per second ([rate limits](https://docs.customer.io/integrations/api/app/#rate-limits)) from one bucket per workspace that every App API call without its own limit draws from, writes included (`components.responses.InboxPreviewReadRateLimited` in the [OpenAPI spec](https://docs.customer.io/files/journeys-app.json)).

**Why this matters:** Leave `matchers` empty: an `HttpRequestRegexMatcher` does not interpolate `url_base`, so it cannot follow the Region host, and one bucket covers every endpoint anyway. The customer's own App API traffic draws from the same bucket, so 429s still happen; at `Retry-After: 1` each retry takes about 2 s, so 30 retries ride out about a minute of them. More workers cannot push a sync past the budget.

## 4. Incremental Sync Is Client-Side With a One-Hour Lookback

All three streams are incremental on `updated` (epoch seconds, `datetime_format: "%s"`) with `is_client_side_incremental: true`, because no list endpoint filters by time: [`listCampaigns`](https://docs.customer.io/integrations/api/app/tag/automations/listcampaigns/) takes no parameters, [`listCampaignActions`](https://docs.customer.io/integrations/api/app/tag/automations/listcampaignactions/) takes only the `start` page cursor and [`listNewsletters`](https://docs.customer.io/integrations/api/app/tag/newsletters/listnewsletters/) takes `limit`, `sort` and `start`. Every sync reads the full lists and emits records whose `updated` is at or after the saved cursor minus `lookback_window: PT1H`. `start_datetime.max_datetime` caps the start at the current time, so a future Start Date syncs nothing instead of failing the check. `campaigns_actions` keeps one cursor per campaign (called an automation in the Customer.io UI), and the CDK starts a new campaign's partition from the stream-wide cursor minus the lookback (`airbyte_cdk/sources/declarative/incremental/concurrent_partition_cursor.py`).

**Why this matters:** The lists are read page by page and are not ordered by `updated`, so a record edited after its page was read, while a later page holds a later edit, falls below the saved cursor; the lookback re-emits it on the next sync, and Append + Deduped absorbs the repeats. It costs no extra requests because every sync reads the full lists anyway. Actions copied into a duplicated campaign are skipped if they keep an `updated` older than the stream-wide cursor minus the lookback; Customer.io does not document whether they do. Do not set `incremental_dependency: true` on the `campaigns_actions` parent: Customer.io does not document that a campaign's `updated` changes when one of its actions changes, so action updates could be skipped.

## 5. `campaigns_actions.id` Is a JSON String

The API returns `campaigns_actions.id` as a JSON string (for example `"18"`) and the schema declares `string`, although the [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) documents an integer. `campaigns.actions[].id` arrives as an integer.

**Why this matters:** Joins between `campaigns.actions[].id` and `campaigns_actions.id` need a cast. Changing the declared type of an existing field is a breaking change.

## 6. `campaigns_actions` Logs a Harmless Parent-State Warning

`campaigns_actions.retriever.partition_router` is a one-element list, so the CDK wraps the `SubstreamPartitionRouter` in a `CartesianProductStreamSlicer` and logs "Parent state handling is not supported for CartesianProductStreamSlicer." on every read.

**Why this matters:** The warning needs no action: the stream does not use parent state (there is no `incremental_dependency`), the parent `campaigns` list is read in full every sync, and the per-campaign cursors live in the stream's own state.
