# Contributing to source-recurly

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Site-wide quota versus per-sync budget** — Recurly shares its request quota across the whole site, but each sync tracks only its own requests. Other connections or integrations can still cause rate limiting.
2. **Reset header is not a retry timer** — The connector deliberately does not wait for Recurly's quota reset time on every retry. Doing so could unnecessarily delay retries for server errors as well as rate limits.
