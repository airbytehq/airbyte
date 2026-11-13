# Contributing to source-recurly

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Site-wide quota versus per-sync budget** — Recurly shares its request quota across the whole site, but each sync tracks only its own requests. Other connections or integrations can still cause rate limiting.
2. **Reset header is not a retry timer** — The connector deliberately does not wait for Recurly's quota reset time on every retry. Doing so could unnecessarily delay retries for server errors as well as rate limits.
3. **Usage Records fan-out** — Every sync scans all subscriptions and fetches usage separately for each subscription add-on. This can use a large share of the site's API quota even when little data has changed.
4. **Positional error-filter coupling** — Feature-aware streams share authentication handling with the base requester. Changes to the order of its error rules can unexpectedly change how these streams handle failures.

## Authentication Decision (A-1)

The connector authenticates with a private API key sent as the HTTP Basic username, as documented in [Recurly API keys](https://docs.recurly.com/docs/api-keys). The Recurly v3 API (`v2021-02-25`) does not document an OAuth flow for third-party integrations, so API-key authentication is the only option.
