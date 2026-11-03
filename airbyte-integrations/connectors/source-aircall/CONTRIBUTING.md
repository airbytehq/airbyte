# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** — Calls, contacts and conversations use configurable date windows to stay under Aircall's per-request result limit.
2. **Cursor choices account for creation-date filters and edits** — Streams use different sync strategies because Aircall filters by creation date, while records may be edited later; numbers and teams are full refresh only; conversations filter on `last_engagement_at` and are incremental on it.
3. **Calls start within Aircall's six-month retention period** — Calls always start 186 days before the sync because older call history is unavailable.
4. **Rate limits are shared across the company** — All workers share Aircall's company-wide limit of 120 requests per minute.
5. **HTTP errors have distinct recovery behavior** — Credential and result-limit errors need configuration changes; rate limits and server errors follow retry behavior.
6. **Pagination differs by endpoint** — Most v1 endpoints start with an omitted page parameter and continue at page 2; campaigns and campaign outcomes follow `meta.next_cursor`, and WhatsApp templates follow `pageInfo.nextToken` per number.
7. **Add-on endpoints are gated by a 403 with a specific body** — Conversations, trackers and WhatsApp templates are skipped only on Aircall's documented feature-gating body; a plain 403 still fails as a credential error.
8. **Primary keys follow Aircall's documented identifiers** — `webhooks` uses `webhook_id` rather than the legacy `id`, and `company` stays keyless because Aircall returns one company object with no identifier.

## Testing

The GSM test key is revoked. Connector behavior is covered by mock-server tests in `unit_tests/`; do not make live Aircall API calls.
