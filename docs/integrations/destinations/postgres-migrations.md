# Postgres Migration Guide

## Upgrading to 3.0.0

This version introduces [Direct Load](/platform/using-airbyte/core-concepts/direct-load-tables) architecture, which writes data directly to final tables without using intermediate raw tables. This provides improved performance and reduced storage costs.

### Key changes

- **No more raw tables by default**: Data is now written directly to final tables. Raw tables are no longer created unless you explicitly enable the "Raw tables only" option.
- **New metadata columns**: Final tables now include `_airbyte_meta` (JSONB) and `_airbyte_generation_id` (BIGINT) columns instead of `_airbyte_loaded_at`.
- **Improved performance**: Direct writes to final tables reduce storage overhead and improve sync performance.

### Migration steps

1. **If you only use final tables**: No action required. Your syncs will automatically use the new Direct Load architecture.

2. **If you depend on raw tables**: Enable the "Raw tables only" option in the connector configuration before upgrading. This will maintain backward compatibility with existing workflows that read from raw tables.

3. **If you have downstream processes**: Review any dbt models or SQL queries that reference the old `_airbyte_loaded_at` column or raw tables, and update them accordingly.

### Backward compatibility

Existing raw tables will not be deleted during the upgrade. However, new syncs will not write to raw tables unless you enable the "Raw tables only" option.

## Upgrading to 2.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables
- Preserving [upper case column names](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2/#destinations-v2-implementation-differences)

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).
