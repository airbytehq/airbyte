# Postgres Migration Guide

## Upgrading to 3.0.0

This version introduces [Direct Load](/platform/using-airbyte/core-concepts/direct-load-tables) architecture, which writes data directly to final tables without using intermediate raw tables. This provides improved performance and reduced storage costs.

### Key changes

- **No more raw tables by default**: Data is now written directly to final tables. Raw tables are no longer created unless you explicitly enable the "Raw tables only" option.
- **New metadata columns**: Final tables now include `_airbyte_meta` (JSONB) and `_airbyte_generation_id` (BIGINT) columns instead of `_airbyte_loaded_at`.
- **Improved performance**: Direct writes to final tables reduce storage overhead and improve sync performance.

### Migration steps

1. **If you only use final tables**: No action required. Your syncs will automatically use the new Direct Load architecture.

2. **If you only depend on raw tables**: Enable the "Raw tables only" option in the connector configuration before upgrading. This will maintain backward compatibility with existing workflows that read from raw tables.

3. **If you depend on both raw and final tables**: This is no longer supported. To include both raw and final tables, create another Postgres destination. In the first destination connector, do not enable "Raw tables only". In the second destination connector, enable "Raw tables only". Then, create dual connections for each source that you need to sync to Postgres.

4. **If you have downstream processes**: Review any dbt models or SQL queries that reference the old `_airbyte_loaded_at` column or raw tables, and update them accordingly.

### Backward compatibility

Existing raw tables will not be deleted during the upgrade. However, new syncs will not write to raw tables unless you enable the "Raw tables only" option.

### Removing old raw tables

After upgrading to version 3.0.0 and confirming your syncs are working correctly with Direct Load, you can optionally remove the old raw tables to free up storage space:

1. Verify that your syncs are completing successfully with the new Direct Load architecture.
2. Confirm that any downstream processes (dbt models, SQL queries, etc.) have been updated to use final tables instead of raw tables.
3. Once confirmed, you can safely drop the old raw tables from the `airbyte_internal` schema (or your configured raw table schema).

:::caution

Only remove raw tables after you have verified that all your workflows are working correctly with the new architecture. This action is irreversible.

:::

## Upgrading to 2.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables
- Preserving [upper case column names](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/#destinations-v2-implementation-differences)

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).
