# Databricks Lakehouse Migration Guide

## Upgrading to 4.0.0

This version upgrades Destination Databricks to the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm, which improves performance and reduces warehouse spend. If you have unusual requirements around record visibility or schema evolution, read that document for more information about how Direct-Load differs from Typing and Deduping.

If you do not interact with the raw tables, you can safely upgrade. There is no breakage for this use case. But if you interact with the raw tables, follow the migration steps below.

### Migration steps

1. Raw tables (`_airbyte_raw_*`) are no longer produced. Update any downstream dbt models or SQL queries to reference the final tables instead.
2. Upgrade the destination to version 4.0.0
3. Verify data in the final tables
4. Optional: Drop old raw tables (`_airbyte_raw_*`) after verifying the new tables

## Upgrading to 3.0.0

This version adds an `_airbyte_generation_id` column to the raw and final tables and a `sync_id` entry in `_airbyte_meta`.
For now, these values will always be set to 0 - they will be used by the upcoming refreshes feature.

There is no automated upgrade process. After selecting `Upgrade`, you should:

1. `DROP` any raw/final tables created using a 2.x sync
1. Clear (reset) your connection to resync all your data

## Upgrading to 2.0.0

More to come. this is a preview release.

This version introduces [Destinations V2](/release_notes/self-managed/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures.
To review the breaking changes, and how to upgrade, see the [quick start to upgrading](/release_notes/self-managed/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through in the [downstream transformations guide](/release_notes/self-managed/upgrading_to_destinations_v2/#updating-downstream-transformations).
Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 in the [Typing & Deduping guide](/platform/using-airbyte/core-concepts/typing-deduping).
