# source-openai-ads: Unique Connector Behaviors

## 1. API-Key Authentication and OAuth Roadmap

The connector currently authenticates with an API key, and each OpenAI Ads API key is scoped to one ad account ([authentication](https://developers.openai.com/ads/api-reference/authentication)). The [OpenAPI security scheme](https://developers.openai.com/ads/openapi.json#/components/securitySchemes/AdsOAuth) declares an OAuth authorization-code flow, but the connector does not implement OAuth yet. OAuth support is tracked as step 1b on the [certification epic](https://github.com/airbytehq/airbyte-internal-issues/issues/18388).

**Why this matters:** Do not describe the API as inherently API-key-only or add an OAuth configuration without completing the tracked OAuth work.

## 2. Vendor Error Mapping

The [OpenAPI spec](https://developers.openai.com/ads/openapi.json) documents only `200` responses and no error schema. For a `403` on `/ad_account/spend_limit_windows`, the connector reads the vendor's `error.message` and caps it at 300 characters; a string-valued `error` fallback is capped the same way. `429` responses are retried, honoring `Retry-After` before exponential backoff ([rate limits](https://developers.openai.com/ads/api-overview#rate-limits)), and `5xx` responses use the CDK default retry behavior.

A `404` from `/conversions/pixels` is ignored because pixel management may not be enabled for the account ([partner setup](https://developers.openai.com/ads/api-partner-setup)). A `403` from `/ad_account/spend_limit_windows` is ignored because the endpoint requires postpaid invoice billing and billing permission ([ad account](https://developers.openai.com/ads/api-reference/ad-account)). Other responses use the CDK default mapping: `401` and `403` fail as configuration errors, and other `404` responses fail.

**Why this matters:** Keep the two endpoint-specific ignores scoped to their requesters; broadening either filter could hide unrelated permissions or missing-resource failures.

## 3. Shared 600-Request Rate Limit

OpenAI documents limits of 600 requests per minute per endpoint and 1,200 per minute overall, enforced per ad account and per IP ([rate limits](https://developers.openai.com/ads/api-overview#rate-limits)). The connector uses one 600-per-minute `MovingWindowCallRatePolicy` with no matchers. The CDK assigns each request to one policy, so the per-endpoint and overall limits cannot both be modeled; the single global limit remains under both.

Airbyte Cloud connections share egress IPs, so their IP-scoped quota is shared ([Cloud IP allow list](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist)). The connector does not declare a `ratelimit_remaining_header`: the actual vendor header names have not been verified without a test credential.

**Why this matters:** Raising the single global policy above 600 requests per minute could exceed OpenAI's per-endpoint limit, and a Cloud connection's IP quota is shared with other connections.

## 4. Full-Refresh Entities and Incremental Reports

The eight entity streams (`ad_account`, `campaigns`, `ad_groups`, `ads`, `conversion_event_settings`, `conversion_pixels`, `custom_audiences`, and `spend_limit_windows`) are full refresh because their list endpoints do not accept an updated-since filter; the OpenAPI parameters include list filters such as `limit`, `after`, `before`, `order`, `name`, and `include`, but no update-time filter ([OpenAPI spec](https://developers.openai.com/ads/openapi.json)).

Insights and conversions report streams are incremental on `readable_time` and `date`, respectively. They use 14-day slices, a default 32-day lookback, and an end date clamped to the current UTC-12 date to avoid requesting a future date in any account timezone ([insights API](https://developers.openai.com/ads/api-reference/insights), [reporting](https://developers.openai.com/ads/reporting)).

**Why this matters:** Adding an incremental cursor to an entity stream would not make the API return only changed records; report windows and lookback behavior must remain aligned with the vendor's date-based endpoints.

## 5. Endpoint-Specific Pagination Limits

List endpoints use `CursorPagination` with `limit` and `after` request parameters, and `has_more` and `last_id` response fields. The page size is 500 for list endpoints and 2,000 for insights, matching their OpenAPI limits ([OpenAPI spec](https://developers.openai.com/ads/openapi.json)). `/ad_account` and `/ad_account/spend_limit_windows` are unpaginated.

`POST /conversions/insights` has no cursor and rejects responses over 2,000 rows, so the connector requests one entity at a time ([insights API](https://developers.openai.com/ads/api-reference/insights)).

**Why this matters:** Do not add cursor pagination to the conversions endpoint or assume the same page-size ceiling applies to every stream.

## 6. Mock-Only Testing

There is no test credential or vendor sandbox for this connector; certification work tracks this gap in [issue 18389](https://github.com/airbytehq/airbyte-internal-issues/issues/18389). Unit tests use `requests_mock` for API responses. Live reads and `check` are not part of local verification.

**Why this matters:** New endpoint behavior must be covered with deterministic mocked responses until a test credential or sandbox is available.
