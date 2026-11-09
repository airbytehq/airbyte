# Contributing to source-recurly

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication Decision (A-1)

The connector authenticates with a private API key sent as the HTTP Basic username, as documented in [Recurly API keys](https://docs.recurly.com/docs/api-keys). The Recurly v3 API (`v2021-02-25`) does not document an OAuth flow for third-party integrations, so API-key authentication is the only option.

## Rate Limits and Retries

Recurly documents 400 requests/minute for sandbox sites and 1,000 GET requests/minute for production sites, enforced over a sliding five-minute window (`X-RateLimit-Limit` reports 2,000 for sandbox). The `api_budget` paces requests to 2,000 or 5,000 per five minutes based on `is_sandbox`, and matches every `GET` to `https://v3.recurly.com`.

The base requester has a single `DefaultErrorHandler`:

- HTTP 401 and 403 fail as config errors with instructions for finding a valid API key.
- HTTP 429 waits until the epoch timestamp in `X-RateLimit-Reset`, then retries.
- Other retryable responses back off exponentially (factor 5).

The budget declares `X-RateLimit-Reset`, so a 429 does not also fill the moving-window bucket; the error handler alone owns the wait in that case.

## Concurrency

`num_workers` still accepts 1 for existing connections, but the effective concurrency is clamped to at least 2, the lowest level the concurrent CDK runs safely with.

## Config Migration

`begin_time` and `end_time` must end in `Z`. Configs saved before that pattern was enforced are normalized by appending `Z` through `config_normalization_rules`.
