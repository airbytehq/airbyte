# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** - Calls and contacts read date windows with separate settings; calls split a window that still holds too many records, contacts fail with a config error.
2. **Cursor choices account for creation-date filters and edits** - Streams use different sync strategies because Aircall filters by creation date, while records may be edited later.
3. **Calls start within Aircall's six-month retention period** - A first sync or full refresh of calls starts 186 days back because older history is unavailable; incremental syncs start three days before the saved cursor.
4. **Rate limits are shared across the company** - All workers share one budget of 100 requests per minute, below Aircall's company-wide limit of 120.
5. **HTTP errors have distinct recovery behavior** - Credential errors and the contacts result limit need configuration changes; rate limits and server errors follow retry behavior.
6. **V1 page numbering starts at one** - V1 pagination starts with an omitted page parameter and continues at page 2.

## Testing

`unit_tests/` holds mock-server tests that need no Aircall account. The acceptance tests read the CI secret `SECRET_SOURCE-AIRCALL__CREDS`.
