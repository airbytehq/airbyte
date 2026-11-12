# Contributing to source-recurly

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication Decision (A-1)

The connector authenticates with a private API key sent as the HTTP Basic username, as documented in [Recurly API keys](https://docs.recurly.com/docs/api-keys). The Recurly v3 API (`v2021-02-25`) does not document an OAuth flow for third-party integrations, so API-key authentication is the only option.

## Rate Limits and Retries

Recurly documents 400 requests/minute for sandbox sites and 1,000 GET requests/minute for production sites, enforced over a sliding five-minute window (`X-RateLimit-Limit` reports 2,000 for sandbox). The `api_budget` paces requests to 2,000 or 5,000 per five minutes based on `is_sandbox`, and matches every `GET` to `https://v3.recurly.com`. The budget is per sync, while Recurly's limit is per site, so other connections or integrations using the same site can still cause HTTP 429 responses.

The base requester has a single `DefaultErrorHandler`:

- HTTP 401 and 403 fail as config errors with instructions for finding a valid API key.
- HTTP 429 and other retryable responses back off exponentially (factor 5, five retries: about 11, 21, 41, 81 and 161 seconds), which covers Recurly's five-minute window.

The handler does not use `WaitUntilTimeFromHeader` on `X-RateLimit-Reset`. Recurly sends that header on every response, and the CDK applies backoff strategies to every retryable response, so a header-based wait would also delay 5xx retries by up to five minutes. A `CompositeErrorHandler` does not help, because it merges the backoff strategies of its child handlers into one list.

The budget declares `X-RateLimit-Reset`, so `MovingWindowCallRatePolicy` ignores the response headers instead of marking its bucket full after a 429.

## Config Migration

`begin_time` and `end_time` must end in `Z`. Configs saved before that pattern was enforced are normalized by appending `Z` through `config_normalization_rules`.
