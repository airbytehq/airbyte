# Redshift Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 is a full rewrite of the Redshift destination using the new CDK architecture. Key changes:

> We encourage upgrading to 4.0.0 — it speeds up Airbyte syncs and reduces warehouse costs by skipping the separate typing and deduping queries.

- **No raw tables** — data is written directly to final tables instead of staging through `_airbyte_raw_*` tables
- **Improved data validation** — oversized or out-of-range values (VARCHAR > 65,535 bytes, SUPER > 16 MB, NUMERIC precision > 38) are now nullified before insertion and tracked in the `_airbyte_meta` column
- **Updated dependencies** — uses Redshift JDBC driver 2.1.0.30 and AWS SDK v2 (2.31.1)

### Migration steps

1. Update any downstream dbt models or SQL queries that reference `_airbyte_raw_*` tables
2. Upgrade the destination to version 4.0.0
3. Verify data in the final tables
4. Optional: Drop old raw tables (`_airbyte_raw_*`) after verifying the new tables

## Upgrading to 3.0.0

This version removes support for standard inserts. Although this loading method is easier to set up than S3 staging, it has two major disadvantages:

- Standard inserts is significantly slower
- Standard inserts is significantly more expensive

[Redshift's documentation](https://docs.aws.amazon.com/redshift/latest/dg/r_INSERT_30.html#r_INSERT_30_usage_notes) states:
> We strongly encourage you to use the COPY command to load large amounts of data. Using individual INSERT statements to populate a table might be prohibitively slow.

See our [Redshift docs](https://docs.airbyte.com/integrations/destinations/redshift#for-copy-strategy) for more information on how to set up S3 staging.

## Upgrading to 2.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).
