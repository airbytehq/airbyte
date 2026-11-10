# Contributing to source-revenuecat

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Pagination follows the vendor's `next_page` path** -- The connector requests the exact next-page path RevenueCat returns. Re-parsing the cursor encodes anonymous IDs twice and makes syncs loop forever.
2. **Incremental sync is client-side only** -- RevenueCat lists have no date filter or sort order, so every sync reads all pages and filters by the saved state locally. Never stop paging early.
3. **Rate limits differ by endpoint domain, and customer substreams fan out** -- Customer endpoints allow 480 requests per minute, configuration endpoints 60 and metrics 25. Per-customer streams make large projects slow, so the heartbeat timeout is one hour.
4. **`metrics_overview` is a point-in-time snapshot** -- It returns current metric values with no paging and no usable cursor, so it stays full refresh.
5. **Known defects held for a major release** -- Some primary keys, cursors and identifier types are wrong but can only be fixed in a breaking release.

## Testing

There are no test credentials for this connector, so acceptance tests other than `spec` are bypassed. Cover changes with the mock server tests in `unit_tests/mock_server/` (`poe test-unit-tests`).
