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

3. Open the **Optional fields** section.

4. Turn on **Disable Final Tables**.

5. Click **Test and save**.

:::note
After upgrading to version 4, this setting appears as **Legacy raw tables** and remains enabled.
:::

#### If you interact with both raw and final tables

If you interact with both the raw _and_ final tables, this use case is no longer supported. Instead, create two connectors. One with `Disable Final Tables` turned on, and one with it turned off. Starting now, you must run the two connections in parallel.

1. In the navigation bar, click **Destinations**.

2. For each Snowflake destination you have, add an identical second Snowflake destination.

3. Ensure each pair of Snowflake connectors have opposite settings for **Disable Final Tables**. One connector should have this setting turned on, and the other should have it turned off.

4. Configure distinct default schemas for each destination to avoid table name collisions:

   - For the destination that creates final tables, set a distinct **Schema** in the Snowflake destination configuration. For example, `ANALYTICS_FINAL_TABLES`. This is where Airbyte writes final tables.

   - For the raw-only destination (with **Disable Final Tables** turned on), set a distinct **Airbyte Internal Table Dataset Name** under the **Advanced** section (for example, `AIRBYTE_INTERNAL_RAW`). This is where Airbyte writes raw tables.

   - Example configuration:

     - Destination A (final tables): Schema = `ANALYTICS_FINAL_TABLES`, Airbyte Internal Table Dataset Name = `AIRBYTE_INTERNAL`

     - Destination B (raw tables): Airbyte Internal Table Dataset Name = `AIRBYTE_INTERNAL_RAW`

   - Using distinct schemas prevents table name collisions when running both destinations in parallel.

5. Recreate your connections to point to the appropriate destination.

   - Connections that need raw tables only should target the destination with **Disable Final Tables** turned on.

   - Connections that need final tables should target the destination with this setting turned off.

6. Run test syncs on both destinations to verify outputs.

   - The raw tables destination should write only to the internal schema. Default: `airbyte_internal`.

   - The standard destination should write only final tables to the target schema.

7. After verifying that both destinations work correctly, continue running both connections in parallel going forward.

### Do the upgrade

Follow the standard [connector upgrade steps](#how-to-upgrade) shown below.

### Optional: remove legacy raw tables

The version 4 connector doesn't automatically remove tables created by earlier versions. After upgrading to version 4 and verifying your data, you can optionally remove the old raw tables.

You can find the raw tables in the schema configured as **Airbyte Internal Table Dataset Name**. This defaults to `airbyte_internal`. If you customized this setting, look in that schema instead.

The table names match these patterns depending on which version created them:

- **Before version 4:**: `raw_{namespace}__{stream}` (for example, `airbyte_internal.raw_public__users`)

- **Version 4 with legacy raw tables mode**: `{namespace}_raw__stream_{stream}` (for example, `airbyte_internal.public_raw__stream__users`)

The number of underscores between `raw` and `stream` may vary depending on the longest underscore sequence in your namespace and stream names.

:::note
Version 4 of the Snowflake destination uses the `airbyte_internal` schema for temporary scratch space. For example, Airbyte needs this for streams running in dedup mode, truncate refreshes, and overwrite syncs. Dropping the entire `airbyte_internal` schema can interrupt active syncs and cause data loss. Only drop the specific raw tables you no longer need.
:::

To remove the old raw tables:

1. **Pause or allow active syncs to complete** before dropping any tables to avoid interrupting data transfers.

2. **List candidate raw tables** to identify which tables to remove:

   ```sql
   -- For Version 2/3 raw tables:
   SHOW TABLES IN SCHEMA <DATABASE>.<INTERNAL_SCHEMA> LIKE 'RAW\_%';

   -- For Version 4 legacy raw tables:
   SHOW TABLES IN SCHEMA <DATABASE>.<INTERNAL_SCHEMA> LIKE '%RAW%STREAM%';
   ```

   Replace `<DATABASE>` with your Snowflake database name and `<INTERNAL_SCHEMA>` with your internal schema name (default `airbyte_internal`).

3. **Drop specific raw tables** you no longer need:

   ```sql
   DROP TABLE IF EXISTS <DATABASE>.<INTERNAL_SCHEMA>.<TABLE_NAME>;
   ```

   Replace `<TABLE_NAME>` with the specific table name you want to remove. Use fully qualified names (database.schema.table) to avoid ambiguity.

### Update downstream pipelines

If you have downstream apps and resources that interact with raw tables, update them to reference any new schema and table names.

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

## How to upgrade {#how-to-upgrade}

<MigrationGuide />
