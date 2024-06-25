---
products: all
---

# Schema Change Management

You can specify for each connection how Airbyte should handle any change of schema in the source. This process helps ensure accurate and efficient data syncs, minimizing errors and saving you time and effort in managing your data pipelines.

## Types of Schema Changes

When propagation is enabled, your data in the destination will automatically shift to bring in the new changes.

| Type of Schema Change    | Propagation Behavior                                                                                                                                                                                                                                                                                                                                             |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| New Column               | The new colummn will be created in the destination. Values for the column will be filled in for the updated rows. If you are missing values for rows not updated, a backfill can be done by completing a full resync or through the `Backfill new or renamed columns` option (see below)                                                                         |
| Removal of column        | The old column will be removed from the destination.                                                                                                                                                                                                                                                                                                             |
| New stream               | The first sync will create the new stream in the destination and fill all data in as if it is an initial sync.                                                                                                                                                                                                                                                   |
| Removal of stream        | The stream will stop updating, and any existing data in the destination will remain.                                                                                                                                                                                                                                                                             |
| Column data type changes | The data in the destination will remain the same. For those syncing on a Destinations V2 destination, any new or updated rows with incompatible data types will result in a row error in the destination tables and show an error in the `airbyte_meta` field. You will need to refresh the schema and do a full resync to ensure the data types are consistent. |

## Detect and Propagate Schema Changes

Based on your configured settings for **Detect and propagate schema changes**, Airbyte will automatically sync those changes or ignore them:

| Setting                                    | Description                                                                                                                                                                                                                                |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Propagate all changes (streams and fields) | All new streams and column changes from the source will automatically be propagated and reflected in the destination. This includes stream changes (additions or deletions), column changes (additions or deletions) and data type changes |
| Propagate column changes only              | Only column changes will be propagated. New or removed streams are ignored.                                                                                                                                                                |
| Detect changes and manually approve        | Schema changes will be detected, but not propagated. Syncs will continue running with the schema you've set up. To propagate the detected schema changes, you will need to approve the changes manually                                    |
| Detect changes and pause connection        | Connections will be automatically disabled as soon as any schema changes are detected                                                                                                                                                      |

Airbyte currently checks for any changes in your source schema immediately before syncing, at most once every 24 hours. This means that your schema may not always be propagated before your sync.

:::tip
Ensure you receive schema notifications for your connection by enabling notifications in the connection's settings.
:::

In all cases, if a breaking schema change is detected, the connection will be paused immediately for manual review to prevent future syncs from failing. Breaking schema changes occur when:

- An existing primary key is removed from the source
- An existing cursor is removed from the source

To re-enable the streams, ensure the correct **Primary Key** and **Cursor** are selected for each stream and save the connection. You will be prompted to clear the affected streams so that Airbyte can ensure future syncs are successful.

### Backfill new or renamed columns

To further automate the propagation of schema changes, Airbyte also offers the option to backfill new or renamed columns as a part of the sync. This means that anytime a new column is detected through the auto-propagation of schema changes, Airbyte will sync the entire stream again so that all values in the new columns will be completely filled, even if the row was not updated. If this option is not enabled, only rows that are updated as a part of the regular sync will be populated with a value.

This feature will only perform the backfill when `Detect and propagate schema changes` is set to `Propagate all changes` or `Propagate columns changes only` and Airbyte detects the schema change as a part of a sync. Refreshing the schema manually and applying schema changes will not allow the backfill to occur.

:::tip
Enabling automatic backfills may incur increased destination costs from refreshing the entire stream.
:::

For Cloud users, any stream that contains a new or renamed column will not be billed and the free usage will be noted on the billing page. Streams that are synced in the same sync and do not contain a new or renamed column will be billed as usual.

## Review non-breaking schema changes

If the connection is set to **Detect any changes and manually approve** schema changes, Airbyte continues syncing according to your last saved schema. You need to manually approve any detected schema changes for the schema in the destination to change.

1. In the Airbyte UI, click **Connections**. Select a connection and navigate to the **Schema** tab. If schema changes are detected, you'll see a blue "i" icon next to the Replication ab.

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes detected.

4. Review the changes and click **OK** to close the dialog.

5. Scroll to the bottom of the page and click **Save changes**.

## Resolving breaking changes

Breaking changes require your attention to resolve. They may immediately cause the connection to be disabled if your source changed. When a breaking change occurs due to a new major connector version, you can upgrade the connector manually within a time period once reviewing the changes.

A connection will always automatically be disabled if an existing primary key or cursor field is removed. You must review and fix the changes before editing the connection or resuming syncs.

Breaking changes can also occur when a new major version of the connector is released. In these cases, the connection will alert you of a breaking change but continue to sync until the cutoff date for upgrade. On the cutoff date, the connection will automatically be disabled on that date to prevent failure or unexpected behavior. It is **highly recommended** to upgrade before the cutoff date to ensure you continue syncing without interruption.

A major version upgrade will include a breaking change if any of these apply:

| Type of Change                            | Description                                                                                                                     |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Connector Spec Change                     | The configuration has been changed and syncs will fail until users reconfigure or re-authenticate.                              |
| Schema Change                             | The type of property previously present within a record has changed and a refresh of the source schema is required.             |
| Stream or Property Removal                | Data that was previously being synced is no longer going to be synced                                                           |
| Destination Format / Normalization Change | The way the destination writes the final data or how Airbyte cleans that data is changing in a way that requires a full refresh |
| State Changes                             | The format of the source’s state has changed, and the full dataset will need to be re-synced                                    |

To review and fix breaking schema changes:

1. In the Airbyte UI, click **Connections** and select the connection with breaking changes.

2. Review the description of what has changed in the new version. The breaking change will require you to upgrade your source or destination to a new version by a specific cutoff date.

3. Update the source or destination to the new version to continue syncing. Follow the connector-specific migration guide to ensure your connections continue syncing successfully.

### Manually refresh the source schema

In addition to Airbyte's automatic schema change detection, you can manually refresh the source schema to stay up to date with changes in your schema. To manually refresh the source schema:

1.  In the Airbyte UI, click **Connections** and then click the connection you want to refresh. Click the **Schema** tab.

2.  In the **Select streams** table, click **Refresh source schema** to fetch the schema of your data source.

3.  If there are changes to the schema, you can review them in the **Refreshed source schema** dialog.
