# Manage schema changes

You can specify for each connection how Airbyte should handle any change of schema in the source. This process helps ensure accurate and efficient data syncs, minimizing errors and saving you time and effort in managing your data pipelines.

Airbyte checks for any changes in your source schema immediately before syncing, at most once every 24 hours.

Based on your configured settings for **Detect and propagate schema changes**, Airbyte will automatically sync those changes or ignore them: 

| Setting              | Description                                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------------------------------|
| Propagate all changes | All new tables and column changes from the source will automatically be propagated and reflected in the destination. This includes stream changes (additions or deletions), column changes (additions or deletions) and data type changes
| Propagate column changes only (default) | Only column changes will be propagated
| Ignore | Schema changes will be detected, but not propagated. Syncs will continue running with the schema you've set up. To propagate the detected schema changes, you will need to approve the changes manually | 
| Pause Connection | Connections will be automatically disabled as soon as any schema changes are detected |

When propagation is enabled, your data in the destination will automatically shift to bring in the new changes. 

| Type of Schema Change              | Propagation Behavior                                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------------------------------|
| New Column | The new colummn will be created in the destination. Values for the column will be filled in for the updated rows. If you are missing values for rows not updated, a backfill can be done by completing a full resync.
| Removal of column | The old column will be removed from the destination.
| New stream | The first sync will create the new stream in the destination and fill all data in as if it is a historical sync. | 
| Removal of stream | The stream will stop updating, and any existing data in the destination will remain. |
| Column data type changes | The data in the destination will remain the same. Any new or updated rows with incompatible data types will result in a row error in the raw Airbyte tables. You will need to refresh the schema and do a full resync to ensure the data types are consistent. 

In all cases, if a breaking schema change is detected, the connection will be paused immediately for manual review to prevent future syncs from failing. Breaking schema changes occur when:
* An existing primary key is removed from the source
* An existing cursor is removed from the source

To re-enable the streams, ensure the correct **Primary Key** and **Cursor** are selected for each stream and save the connection. 

## Review non-breaking schema changes

If the connection is set to **Ignore** any schema changes, Airbyte continues syncing according to your last saved schema. You need to manually approve any detected schema changes for the schema in the destination to change.

1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections**. Select a connection and navigate to the **Replication** tab. If schema changes are detected, you'll see a blue "i" icon next to the Replication ab. 

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes detected. 

4. Review the changes and click **OK** to close the dialog.

5. Scroll to the bottom of the page and click **Save changes**.

## Resolving breaking changes

Breaking changes require your attention to resolve. They may immediately cause the connection to be disabled, or you can upgrade the connector manually within a time period once reviewing the changes.

A connection will always automatically be disabled if an existing primary key or cursor field is removed. You must review and fix the changes before editing the connection or resuming syncs.

Breaking changes can also occur when a new version of the connector is released. In these cases, the connection will alert you of a breaking change but continue to sync until the cutoff date for upgrade. On the cutoff date, the connection will automatically be disabled on that date to prevent failure or unexpected behavior. It is **highly recommended** to upgrade before the cutoff date to ensure you continue syncing without interruption.

A major version upgrade will include a breaking change if any of these apply:

| Type of Change   | Description                                                                                                         |
|------------------|---------------------------------------------------------------------------------------------------------------------|
| Connector Spec Change         | The configuration has been changed and syncs will fail until users reconfigure or re-authenticate.              |
| Schema Change            | The type of property previously present within a record has changed and a refresh of the source schema is required.
| Stream or Property Removal          | Data that was previously being synced is no longer going to be synced              |
| Destination Format / Normalization Change          | The way the destination writes the final data or how Airbyte cleans that data is changing in a way that requires a full refresh                |
| State Changes          | The format of the source’s state has changed, and the full dataset will need to be re-synced                |

To review and fix breaking schema changes:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection with breaking changes.

2. Review the description of what has changed in the new version. The breaking change will require you to upgrade your source or destination to a new version by a specific cutoff date. 

3. Update the source or destination to the new version to continue syncing. 

### Manually refresh the source schema

In addition to Airbyte Cloud’s automatic schema change detection, you can manually refresh the source schema to stay up to date with changes in your schema. 

 To manually refresh the source schema:

 1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to refresh.

 2. Click the **Replication** tab.

 3. In the **Activate the streams you want to sync** table, click **Refresh source schema** to fetch the schema of your data source.

 4. If there are changes to the schema, you can review them in the **Refreshed source schema** dialog.

## Manage Schema Change Notifications
[Refer to our notification documentation](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications#enable-schema-update-notifications) to understand how to stay updated on any schema updates to your connections.