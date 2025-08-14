# Change Data Capture (CDC)

## What is log-based incremental replication?

Many common databases support writing all record changes to log files for the purpose of replication. A consumer of these log files \(such as Airbyte\) can read these logs while keeping track of the current position within the logs in order to read all record changes coming from `DELETE`/`INSERT`/`UPDATE` statements.

## Syncing

The orchestration for syncing is similar to non-CDC database sources. After selecting a sync interval, syncs are launched regularly. We read data from the previously synced position in the logs up to the start time of the sync. We do not treat CDC sources as infinite streaming sources. You should ensure that your schedule for running these syncs is frequent enough to consume the logs that are generated. The first time the sync is run, a snapshot of the current state of the data will be taken. This snapshot is created with a `SELECT` statement and is effectively a Full Refresh (meaning changes won't be logged). Subsequent syncs will use the logs to determine which changes took place since the last sync and update those. Airbyte keeps track of the current log position between syncs.

A single sync might have some tables configured for Full Refresh replication and others for Incremental. If CDC is configured at the source level, all tables with Incremental selected will use CDC. All Full Refresh tables will replicate using the same process as non-CDC sources.

The Airbyte Protocol outputs records from sources. Records from `UPDATE` and `DELETE` statements appear the same way as records from `INSERT` statements. We support different options for how to sync this data into destinations using primary keys, so you can choose to append this data, delete in place, etc.

We add some metadata columns for CDC sources which all begin with the `_ab_cdc_` prefix. The actual columns synced will vary per source, but might look like:

- `_ab_cdc_lsn` of `_ab_cdc_cursor` the point in the log where the record was retrieved
- `_ab_cdc_log_file` & `_ab_cdc_log_pos` \(specific to mysql source\) is the file name and position in the file where the record was retrieved
- `_ab_cdc_updated_at` is the timestamp for the database transaction that resulted in this record change and is present for records from `DELETE`/`INSERT`/`UPDATE` statements
- `_ab_cdc_deleted_at` is the timestamp for the database transaction that resulted in this record change and is only present for records from `DELETE` statements

## Limitations

- CDC incremental is only supported for tables with primary keys for most sources. A CDC source can still choose to replicate tables without primary keys as Full Refresh or a non-CDC source can be configured for the same database to replicate the tables without primary keys using standard incremental replication.
- Data must be in tables, not views.
- The modifications you are trying to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made from `TRUNCATE`/`ALTER` won't appear in logs and therefore in your destination.
- Newly created tables/collections in your schema will cause the CDC snapshot to be ahead of what Airbyte has in the connection state. A refresh is required after any new table/collection is added.
- There are database-specific limitations. See the documentation pages for individual connectors for more information.
- The final table will not show the records whose most recent entry has been deleted, as denoted by _ab_cdc_deleted_at.

### Adding New Schemas/Columns

When using CDC, each schema included in the sync will first undergo an initial snapshot (equivalent to a full refresh).

If you create a new schema/column that is not yet being synced, **it must first be snapshotted** before CDC can begin tracking changes.
Upon schema updates, you should see a _**Schema changes detected**_ notice in the _Schema_ section.
If the schema/column is not visible, click _**Refresh source schema**_ to retrieve the latest structure from your source.

CDC tracks changes only for schemas that are included in the sync. To add a new schema/column:
1. Review and approve the new changes.
2. Enable the newly added schema(s)/column(s).
3. Navigate to the _Status_ page and trigger a refresh:
    - **For new schemas**: Locate the newly added schema, click the three dots (⋮) next to it, and choose _Refresh Stream_.
    - **For new columns**: Locate the schema containing the new column(s), click the three dots (⋮) next to it, and choose _Refresh Stream_.

To avoid unintentional sync issues, we recommend enabling `Approve all schema changes myself` under the
_Detect and propagate schema changes_ in the _Setting_ section. This prevents newly added detected changes from being included in the sync without a proper snapshot,
reducing the risk of LSN issues and sync failures.

:::tip

Adding new schemas/columns to a CDC-enabled database does **not** automatically enable CDC tracking on them.
We recommend manually verifying that CDC is enabled on any newly added database objects. Since each source database uses different commands to configure and verify CDC, be sure to follow the appropriate steps for your specific database.
For an example of how to enable CDC on a new schema in MSSQL, visit our [MSSQL Troubleshooting](https://docs.airbyte.com/integrations/sources/mssql/mssql-troubleshooting) page.

:::

## Current Support

- [Postgres](/integrations/sources/postgres) \(For a quick video overview of CDC on Postgres, click [here](https://www.youtube.com/watch?v=NMODvLgZvuE&ab_channel=Airbyte)\)
- [MySQL](/integrations/sources/mysql)
- [Microsoft SQL Server / MSSQL](/integrations/sources/mssql)
- [MongoDB](/integrations/sources/mongodb-v2)
- [Oracle DB](/integrations/enterprise-connectors/source-oracle-enterprise)
- [SAP HANA](/integrations/enterprise-connectors/source-sap-hana)
- [IBM Db2](/integrations/enterprise-connectors/source-db2)

## Coming Soon


- Please [create a ticket](https://github.com/airbytehq/airbyte/issues/new/choose) if you need CDC support on another database!

## Additional information

- [An overview of Airbyte’s replication modes](https://airbyte.com/blog/understanding-data-replication-modes).
- [Understanding Change Data Capture (CDC): Definition, Methods and Benefits](https://airbyte.com/blog/change-data-capture-definition-methods-and-benefits)
- [Explore Airbyte's Change Data Capture (CDC) synchronization](https://airbyte.com/tutorials/incremental-change-data-capture-cdc-replication)
