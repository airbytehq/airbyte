# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** - Calls, contacts and conversations read date windows; calls split a window that still holds too many records, contacts fail with a config error.
2. **Cursor choices account for creation-date filters and edits** - Streams use different sync strategies because Aircall filters by creation date, while records may be edited later; conversations filter on `last_engagement_at` and are incremental on it.
3. **Calls start within Aircall's six-month retention period** - A first sync or full refresh of calls starts 186 days back because older history is unavailable; incremental syncs start three days before the saved cursor.
4. **Rate limits are shared across the company** - All workers share one budget of 100 requests per minute, below Aircall's company-wide limit of 120.
5. **HTTP errors have distinct recovery behavior** - Credential errors and the contacts result limit need configuration changes; rate limits and server errors follow retry behavior.
6. **Pagination differs by endpoint** - Most v1 endpoints start with an omitted page parameter and continue at page 2; campaigns and campaign outcomes follow `meta.next_cursor`, and WhatsApp templates follow `pageInfo.nextToken` per number.
7. **Add-on endpoints are gated by a 403 with a specific body** - Conversations, trackers and WhatsApp templates are skipped only on Aircall's documented feature-gating body; a plain 403 still fails as a credential error.

## Testing

`unit_tests/` holds mock-server tests that need no Aircall account. The acceptance tests read the CI secret `SECRET_SOURCE-AIRCALL__CREDS`.
