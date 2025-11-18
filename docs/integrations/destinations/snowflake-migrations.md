import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Snowflake Migration Guide

## Upgrading to 4.0.0

This version upgrades the Snowflake destination from using [typing and deduping](/platform/using-airbyte/core-concepts/typing-deduping) to [direct loading](/platform/using-airbyte/core-concepts/direct-load-tables). This upgrade improves performance and reduces warehouse spend. If you have unusual requirements around record visibility or schema evolution, read the documentation for those methodologies for more information about how direct loading differs from typing and deduping.

This version also adds an option to enable CDC deletions as soft deletes.

### Decide how to handle raw tables

The exact steps to begin the migration depend on whether you interact with Airbyte's raw tables in Snowflake.

#### If you don't interact with raw tables

If you don't interact with the raw tables, you can safely upgrade. There's no breaking change for you.

#### If you only interact with raw tables

If you _only_ interact with the raw tables, enable the `Disable Final Tables` option before upgrading. This enables the `Legacy raw tables` option after upgrading.

1. In the navigation bar, click **Destinations**.

2. Open your **Snowflake** connector.

3. <!-- Devin: fill out the rest of these steps to use Disable Final Tables from Snowflake v3 -->

#### If you interact with both raw and final tables

If you interact with both the raw _and_ final tables, this use case is no longer supported. Instead, create two connectors. One with `Disable Final Tables` turned on, and one with it turned off. Starting now, you must run the two connections in parallel.

1. In the navigation bar, click **Destinations**.

2. For each Snowflake destination you have, add an identical second Snowflake destination.

3. Ensure each pair of Snowflake connectors have opposite settings for <!-- Devin: fill out the rest of this step to use Disable Final Tables from Snowflake v3 -->

4. <!-- Devin: fill out the rest of this process -->

<MigrationGuide />

### Optional: clean up legacy raw tables

The version 4.0 connector doesn't automatically remove tables created by earlier versions. After upgrading to version 4 and verifying your data, you can optionally remove the old raw tables.

For most users, You can find the raw tables <!-- Devin: where? -->. The names match the pattern <!-- Devin: what are the tables and schemas called? -->

:::note
Version 4 of the Snowfalke destination uses the `airbyte_internal` database for temporary scratch space (for example, streams running in dedup mode, truncate refreshes, and overwrite syncs). Dropping the entire `airbyte_internal database` can interrupt active syncs and cause data loss. Only drop the specific raw tables you no longer need.
:::

To remove the old raw tables:

<!-- Devin: SQL query to delete a raw table in Snowflake -->

## Upgrading to 3.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).

## Upgrading to 2.0.0

Snowflake no longer supports GCS/S3. Please migrate to the Internal Staging option. This is recommended by Snowflake and is cheaper and faster.
