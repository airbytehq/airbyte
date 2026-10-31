# Contributing to source-bing-ads

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Duplicate Records from Predicate-Based Filtering** — Overlapping account-name predicates can return duplicate accounts; the connector deduplicates them.
2. **Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type** — Bulk downloads can contain plain CSV despite the expected gzip format. Both forms must remain supported.
3. **Signed Download URL Expiration Is Transient** — Expired signed download URLs are temporary failures, not invalid credentials. Genuine permission errors remain configuration errors.
