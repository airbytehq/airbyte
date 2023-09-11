import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import {SnowflakeMigrationGenerator, BigQueryMigrationGenerator} from './destinations_v2.js'

# Upgrading to Destinations V2

## What is Destinations V2?

Airbyte Destinations V2 provides you with:

- One-to-one table mapping: Data in one stream will always be mapped to one table in your data warehouse. No more sub-tables.
- Improved error handling with `_airbyte_meta`: Airbyte will now populate typing errors in the `_airbyte_meta` column instead of failing your sync. You can query these results to audit misformatted or unexpected data.
- Internal Airbyte tables in the `airbyte_internal` schema: Airbyte will now generate all raw tables in the `airbyte_internal` schema. We no longer clutter your destination schema with raw data tables.
- Incremental delivery for large syncs: Data will be incrementally delivered to your final tables. No more waiting hours to see the first rows in your destination table.

To see more details and examples on the contents of the Destinations V2 release, see this [guide](understanding-airbyte/typing-deduping.md). The remainder of this page will walk you through upgrading connectors from legacy normalization to Destinations V2.

Destinations V2 were in preview for Snowflake and BigQuery during August 2023, and launched on August 29th, 2023. Other destinations will be transitioned to Destinations V2 on or before November 1st, 2023.

## Deprecating Legacy Normalization

The upgrade to Destinations V2 is handled by moving your connections to use [updated versions of Airbyte destinations](#destinations-v2-compatible-versions). Existing normalization options, both `Raw data (JSON)` and `Normalized tabular data` will be unsupported starting **Nov 1, 2023**.

![Legacy Normalization](./assets/airbyte_legacy_normalization.png)

As a Cloud user, existing connections using legacy normalization will be paused on **November 1, 2023**. As an Open Source user, you may choose to upgrade at your convenience. However, destination connector versions prior to Destinations V2 will no longer be supported as of **Nov 1, 2023**.

### Breakdown of Breaking Changes

The following table details the delivered data modified by Destinations V2:

| Current Normalization Setting | Source Type                           | Impacted Data (Breaking Changes)                         |
| ----------------------------- | ------------------------------------- | -------------------------------------------------------- |
| Raw JSON                      | All                                   | `_airbyte` metadata columns, raw table location          |
| Normalized tabular data       | API Source                            | Unnested tables, `_airbyte` metadata columns, SCD tables |
| Normalized tabular data       | Tabular Source (database, file, etc.) | `_airbyte` metadata columns, SCD tables                  |

![Airbyte Destinations V2 Column Changes](./assets/destinations-v2-column-changes.png)

Whenever possible, we've taken this opportunity to use the best data type for storing JSON for your querying convenience. For example, `destination-bigquery` now loads `JSON` blobs as type `JSON` in BigQuery (introduced last [year](https://cloud.google.com/blog/products/data-analytics/bigquery-now-natively-supports-semi-structured-data)), instead of type `string`.

## Quick Start to Upgrading

**Self-hosted Airbyte users will need to be on at least version 0.50.24 of the Airbyte Platform.  Update the Airbyte Platform _before_ updating any of the connectors.**

The quickest path to upgrading is to click upgrade on any out-of-date connection in the UI:

![Upgrade Path](./assets/airbyte_destinations_v2_upgrade_prompt.png)

After upgrading the out-of-date destination to a [Destinations V2 compatible version](#destinations-v2-effective-versions), the following will occur at the next sync **for each connection** sending data to the updated destination:

1. Existing raw tables replicated to this destination will be copied to a new `airbyte_internal` schema.
2. The new raw tables will be updated to the new Destinations V2 format.
3. The new raw tables will be updated with any new data since the last sync, like normal.
4. The new raw tables will be typed and de-duplicated according to the Destinations V2 format.
5. Once typing and de-duplication has completed successfully, your previous final table will be replaced with the updated data.

:::caution

Due to the amount of operations to be completed, this first sync after upgrading to Destination V2 **will be longer than normal**. Once your first sync has completed successfully, you may need to make changes to downstream models (dbt, sql, etc.) transforming data. See this [walkthrough of top changes to expect for more details](#updating-downstream-transformations).

:::

Pre-existing raw tables, SCD tables and "unnested" tables will always be left untouched. You can delete these at your convenience, but these tables will no longer be kept up-to-date by Airbyte syncs.
Each destination version is managed separately, so if you have multiple destinations, they all need to be upgraded one by one.

Versions are tied to the destination. When you update the destination, **all connections tied to that destination will be sending data in the Destinations V2 format**. For upgrade paths that will minimize disruption to existing dashboards, see:

- [Upgrading Connections One by One with Dual-Writing](#upgrading-connections-one-by-one-with-dual-writing)
- [Testing Destinations V2 on a Single Connection](#testing-destinations-v2-for-a-single-connection)
- [Upgrading Connections One by One Using CDC](#upgrade-paths-for-connections-using-cdc)
- [Upgrading as a User of Raw Tables](#upgrading-as-a-user-of-raw-tables)
- [Rolling back to Legacy Normalization](#oss-only-rolling-back-to-legacy-normalization)

:::info
If you were a Destinations V2 "Early Access" user, you will still need to opt-into the latest connector version. However, you will not experience the data migration and syncs will continue to work as they have been since the "early access" period began.
:::

## Advanced Upgrade Paths

### Upgrading Connections One by One with Dual-Writing

Dual writing is a method employed during upgrades where new incoming data is written simultaneously to both the old and new systems, facilitating a smooth transition between versions. We recommend this approach for connections where you are especially worried about breaking changes or downtime in downstream systems.

#### Steps to Follow for All Sync Modes

1. **[Open Source]** Update the default destination version for your workspace to a [Destinations V2 compatible version](#destinations-v2-effective-versions). This sets the default version for any newly created destination. All existing syncs will remain on their current version.

![Upgrade your default destination version](assets/airbyte_version_upgrade.png)

2. Create and configure a new destination connecting to the same database as your existing destination except for `Default Schema`, which you should update to a new value to avoid collisions.

![Create a new destination](assets/airbyte_dual_destinations.png)

3. Create a new connection leveraging your existing source and the newly created destination. Match the settings of your pre-existing connection.
4. If the streams you are looking to replicate are in **full refresh** mode, enabling the connection will now provide a parallel copy of the data in the updated format for testing. If any of the streams in the connection are in an **incremental** sync mode, follow the steps below before enabling the connection.

#### Additional Steps for Incremental Sync Modes

These steps allow you to dual-write for connections incrementally syncing data without re-syncing historical data you've already replicated:

1. Copy the raw data you've already replicated to the new schema being used by your newly created connection. You need to do this for every stream in the connection with an incremental sync mode. Sample SQL you can run in your data warehouse:

<Tabs>
  <TabItem value="bigquery" label="BigQuery" default>
    <BigQueryMigrationGenerator />
  </TabItem>
  <TabItem value="snowflake" label="Snowflake">
    <SnowflakeMigrationGenerator />
  </TabItem>
</Tabs>

2. Navigate to the existing connection you are duplicating, and navigate to the `Settings` tab. Open the `Advanced` settings to see the connection state (which manages incremental syncs). Copy the state to your clipboard.

![img.png](assets/airbyte_connection_update_state.png)

3. Go to your newly created connection, replace the state with the copied contents in the previous step, then click `Update State`. This will ensure historical data is not replicated again.
4. Enabling the connection will now provide a parallel copy of all streams in the updated format.
5. You can move your dashboards to rely on the new tables, then pause the out-of-date connection.

### Testing Destinations V2 for a Single Connection

You may want to verify the format of updated data for a single connection. To do this:

1. If all of the streams you are looking to test with are in **full refresh mode**, follow the [steps for upgrading connections one by one](#steps-to-follow-for-all-sync-modes). Ensure any connections you create have a `Manual` replication frequency.
2. For any streams in **incremental** sync modes, follow the [steps for upgrading incremental syncs](#additional-steps-for-incremental-sync-modes). For testing, you do not need to copy pre-existing raw data. By solely inheriting state from a pre-existing connection, enabling a sync will provide a sample of the most recent data in the updated format for testing.

When you are done testing, you can disable or delete this testing connection, and [upgrade your pre-existing connections in place](#quick-start-to-upgrading) or [upgrade one-by-one with dual writing](#upgrading-connections-one-by-one-with-dual-writing).

### Upgrading as a User of Raw Tables

If you have written downstream transformations directly from the output of raw tables, or use the "Raw JSON" normalization setting, you should know that:

- Multiple column names are being updated (from `airbyte_ab_id` to `airbyte_raw_id`, and `airbyte_emitted_at` to `airbyte_extracted_at`).
- The location of raw tables will from now on default to an `airbyte` schema in your destination.
- When you upgrade to a [Destinations V2 compatible version](#destinations-v2-effective-versions) of your destination, we will never alter your existing raw data. Although existing downstream dashboards will go stale, they will never be broken.
- You can dual write by following the [steps above](#upgrading-connections-one-by-one-with-dual-writing) and copying your raw data to the schema of your newly created connection.

We may make further changes to raw tables in the future, as these tables are intended to be a staging ground for Airbyte to optimize the performance of your syncs. We cannot guarantee the same level of stability as for final tables in your destination schema.

### Upgrade Paths for Connections using CDC

For each [CDC-supported](https://docs.airbyte.com/understanding-airbyte/cdc) source connector, we recommend the following:

| CDC Source | Recommendation                                               | Notes                                                                                                                                                                                                                                                |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Postgres   | [Upgrade connection in place](#quick-start-to-upgrading)     | You can optionally dual write, but this requires resyncing historical data from the source. You must create a new Postgres source with a different replication slot than your existing source to preserve the integrity of your existing connection. |
| MySQL      | [All above upgrade paths supported](#advanced-upgrade-paths) | You can upgrade the connection in place, or dual write. When dual writing, Airbyte can leverage the state of an existing, active connection to ensure historical data is not re-replicated from MySQL.                                               |
| SQL Server | [Upgrade connection in place](#quick-start-to-upgrading)     | You can optionally dual write, but this requires resyncing historical data from the SQL Server source.                                                                                                                                               |

## Destinations V2 Compatible Versions

For each destination connector, Destinations V2 is effective as of the following versions:

| Destination Connector | Safe Rollback Version | Destinations V2 Compatible |
| --------------------- | --------------------- | -------------------------- |
| BigQuery              | 1.4.4                 | 2.0.0+                     |
| Snowflake             | 2.0.0                 | 3.0.0+                     |
| Redshift              | 0.4.8                 | 2.0.0+                     |
| MSSQL                 | 0.1.24                | 2.0.0+                     |
| MySQL                 | 0.1.20                | 2.0.0+                     |
| Oracle                | 0.1.19                | 2.0.0+                     |
| TiDB                  | 0.1.3                 | 2.0.0+                     |
| DuckDB                | 0.1.0                 | 2.0.0+                     |
| Clickhouse            | 0.2.3                 | 2.0.0+                     |

Note: If you encounter errors while upgrading from a V1 to a V2 destination, please reach out to support. It may be advantagous to only drop probematic V2 tables rather than to do a full reset, depending on tye type of error.

## Destinations V2 Implementation Differences

In addition to the changes which apply for all destinations described above, there are some per-destination fixes and updates included in Destinations V2:

### BigQuery

1. [Object and array properties](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#the-types) are properly stored as JSON columns. Previously, we had used TEXT, which made querying sub-properties more difficult.
   - In certain cases, numbers within sub-properties with long decimal values will need to be converted to float representations due to a _quirk_ of Bigquery. Learn more [here](https://github.com/airbytehq/airbyte/issues/29594).

## Updating Downstream Transformations

_This section is targeted towards analysts updating downstream models after you've successfully upgraded to Destinations V2._

See here for a [breakdown of changes](#breakdown-of-breaking-changes). Your models will often require updates for the following changes:

#### Column Name Changes

1. `_airbyte_emitted_at_` and `_airbyte_extracted_at` are exactly the same, only the column name changed. You can replace all instances of `_airbyte_emitted_at` with `_airbyte_extracted_at`.
2. `_airbyte_ab_id` and `_airbyte_raw_id` are exactly the same, only the column name changed. You can replace all instances of `_airbyte_ab_id` with `_airbyte_raw_id`.
3. Since `_airbyte_normalized_at` is no longer in the final table. We now recommend using `_airbyte_extracted_at` instead.

#### Data Type Changes

You'll get data type errors in downstream models where previously `string` columns are now JSON. In BigQuery, nested JSON values originating from API sources were previously delivered in type `string`. These are now delivered in type `JSON`.

Example: In dbt, you may now get errors with functions such as `regexp_replace`. You can attempt prepending these with `json_extract_array(...)` or `to_json_string(...)` where appropriate.

#### Stale Tables

Unnested tables (e.g. `public.users_address`) do not get deleted during the migration, and are no longer updated. Your downstream models will not throw errors until you drop these tables. Until then, dashboards reliant on these tables will be stale.
