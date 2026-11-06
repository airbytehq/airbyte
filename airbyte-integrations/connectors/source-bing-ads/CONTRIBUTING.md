# Contributing to source-bing-ads

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Duplicate Records from Predicate-Based Filtering** — An account can match multiple name filters. The connector removes the resulting duplicate account records.
2. **Bulk Report Downloads May Arrive Uncompressed Despite Gzip Content-Type** — Downloaded files can arrive uncompressed despite their advertised format. The connector handles both compressed and uncompressed content.
3. **Bulk Delta Downloads Have a 30-Day Limit** — Old bulk cursors cause full downloads, so the reporting lookback setting does not apply to bulk entities. Inactive accounts can still need full downloads even without lookback. The three new entity streams download newly added accounts in full and enforce an exact timestamp cutoff.
4. **Campaigns and Ads Are Only Returned for Explicitly Requested Types** — The API only returns campaign and ad types that the request lists. The connector requests every documented `CampaignType` and `AdType`, so add new types to both lists when Microsoft introduces them.
5. **Bulk Entity Streams Do Not Cascade Deletions** — Deleting a campaign or ad group does not produce deleted records for its children in the Bulk API. Expired-cursor full downloads can also leave stale destination rows, and parent-derived child fields may remain stale. Use snapshot reconciliation or a separately configured Full Refresh–Overwrite stream when an authoritative current snapshot is required; overwrite removes previous history.
6. **Bulk Entity Downloads Include Diagnostic Error Rows** — The three new entity streams omit companion rows whose `Type` ends in ` Error`, preserving valid entities and deleted records without duplicate IDs from diagnostics.
