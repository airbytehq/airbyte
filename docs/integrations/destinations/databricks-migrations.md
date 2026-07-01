# Databricks Lakehouse Migration Guide

## Upgrading to 4.0.0

This version upgrades Destination Databricks to the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm using the new Bulk CDK, which improves performance and reduces storage costs. If you have unusual requirements around record visibility or schema evolution, read that document for more information about how Direct-Load differs from Typing and Deduping.

### Final table schema changes

This upgrade introduces two schema changes in final tables that may affect downstream consumers:

- **`_airbyte_loaded_at` column removed.** The old connector wrote this timestamp to final tables; the new one does not. Any downstream SQL query or dbt model that selects `_airbyte_loaded_at` should be updated to remove references to this column.
- **`_airbyte_meta` column added.** The old final table schema did not include this column; the new one does. This is additive, so it will not break `SELECT *` queries. However, schema-sensitive downstream consumers — such as strict column-list validations, typed models, or tools that fail on unexpected columns — should be updated to account for it.

### Upgrade guidance

**If you do not interact with raw tables:** You can safely upgrade. Raw tables are no longer produced, but since you don't depend on them, there is no breakage. Review the final table schema changes above and update any affected downstream queries.

**If you _only_ interact with raw tables:** Raw tables (`_airbyte_raw_*`) are no longer produced in Direct-Load mode. You must migrate your downstream queries and dbt models to reference the final tables instead. After upgrading, you may optionally drop the old `_airbyte_raw_*` tables once you have verified the final tables contain the expected data.

**If you interact with both raw _and_ final tables:** You will need to address both sets of changes. Migrate any raw-table queries to use final tables, and update any downstream models that reference `_airbyte_loaded_at` or that are sensitive to the new `_airbyte_meta` column. After upgrading, optionally drop the old raw tables.

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
