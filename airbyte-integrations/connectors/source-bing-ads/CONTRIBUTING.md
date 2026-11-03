# Contributing to source-bing-ads

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Duplicate Records from Predicate-Based Filtering** — An account can match multiple name filters. The connector removes the resulting duplicate account records.
2. **Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type** — Downloaded files can arrive uncompressed despite their advertised format. The connector handles both compressed and uncompressed content.
3. **Bulk Delta Downloads Have a 30-Day Limit** — Old bulk cursors cause full downloads, so the reporting lookback setting does not apply to bulk entities. Inactive accounts can still need full downloads even without lookback.
