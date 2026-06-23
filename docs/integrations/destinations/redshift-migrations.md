# Redshift Migration Guide

## Upgrading to 4.0.0

This version upgrades Destination Redshift to
the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm, which improves performance and
reduces warehouse spend. If you have unusual requirements around record visibility or schema evolution, read that
document for more information about how Direct-Load differs from Typing and Deduping.

If you do not interact with the raw tables, you can safely upgrade. There is no breakage for this use case. But if you
interact with the raw tables, follow the migration steps below.

### Migration steps

1. Raw tables (`_airbyte_raw_*`) are no longer produced. Update any downstream dbt models or SQL queries to reference
   the final tables instead.
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

This version introduces [Destinations V2](/release_notes/self-managed/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see the [quick start to upgrading](/release_notes/self-managed/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through in the [downstream transformations guide](/release_notes/self-managed/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 in the [Typing & Deduping guide](/platform/using-airbyte/core-concepts/typing-deduping).
