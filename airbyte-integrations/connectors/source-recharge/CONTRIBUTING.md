# Contributing to source-recharge

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The `events` Stream Is Hard-Capped to a Rolling 7-Day Window** — Recharge only serves the last
   seven days of events, so the connector floors that stream's start date at seven days ago; a
   historical `start_date`, a saved sync position from a long-paused connection, and any
   `lookback_window_days` setting are all silently overridden for `events` alone. Widening or removing
   that floor makes the API reject the request, which fails the whole sync rather than just this
   stream.
