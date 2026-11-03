# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** — Calls and contacts use configurable date windows to stay under Aircall's per-request result limit.
2. **Cursor choices account for creation-date filters and edits** — Streams use different sync strategies because Aircall filters by creation date, while records may be edited later.
3. **Calls start within Aircall's six-month retention period** — Calls always start 186 days before the sync because older call history is unavailable.
4. **Rate limits are shared across the company** — All workers share Aircall's company-wide limit of 120 requests per minute.
5. **HTTP errors have distinct recovery behavior** — Credential and result-limit errors need configuration changes; rate limits and server errors follow retry behavior.
6. **V1 page numbering starts at one** — V1 pagination starts with an omitted page parameter and continues at page 2.

## Testing

The GSM test key is revoked. Connector behavior is covered by mock-server tests in `unit_tests/`; do not make live Aircall API calls.
