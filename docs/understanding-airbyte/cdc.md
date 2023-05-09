# Change Data Capture (CDC)

## What is log-based incremental replication?

Many common databases support writing all record changes to log files for the purpose of replication. A consumer of these log files \(such as Airbyte\) can read these logs while keeping track of the current position within the logs in order to read all record changes coming from `DELETE`/`INSERT`/`UPDATE` statements.

## Syncing

The orchestration for syncing is similar to non-CDC database sources. After selecting a sync interval, syncs are launched regularly. We read data from the log up to the time that the sync was started. We do not treat CDC sources as infinite streaming sources. You should ensure that your schedule for running these syncs is frequent enough to consume the logs that are generated. The first time the sync is run, a snapshot of the current state of the data will be taken. This is done using `SELECT` statements and is effectively a Full Refresh. Subsequent syncs will use the logs to determine which changes took place since the last sync and update those. Airbyte keeps track of the current log position between syncs.

A single sync might have some tables configured for Full Refresh replication and others for Incremental. If CDC is configured at the source level, all tables with Incremental selected will use CDC. All Full Refresh tables will replicate using the same process as non-CDC sources. However, these tables will still include CDC metadata columns by default.

The Airbyte Protocol outputs records from sources. Records from `UPDATE` statements appear the same way as records from `INSERT` statements. We support different options for how to sync this data into destinations using primary keys, so you can choose to append this data, delete in place, etc.

We add some metadata columns for CDC sources:

* `ab_cdc_lsn` \(postgres and sql server sources\) is the point in the log where the record was retrieved
* `ab_cdc_log_file` & `ab_cdc_log_pos` \(specific to mysql source\) is the file name and position in the file where the record was retrieved
* `ab_cdc_updated_at` is the timestamp for the database transaction that resulted in this record change and is present for records from `DELETE`/`INSERT`/`UPDATE` statements 
* `ab_cdc_deleted_at` is the timestamp for the database transaction that resulted in this record change and is only present for records from `DELETE` statements

## Limitations

* CDC incremental is only supported for tables with primary keys. A CDC source can still choose to replicate tables without primary keys as Full Refresh or a non-CDC source can be configured for the same database to replicate the tables without primary keys using standard incremental replication.
* Data must be in tables, not views.
* The modifications you are trying to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made from `TRUNCATE`/`ALTER`  won't appear in logs and therefore in your destination.
* We do not support schema changes automatically for CDC sources. We recommend resetting and resyncing data if you make a schema change.
* There are database-specific limitations. See the documentation pages for individual connectors for more information.
* The records produced by `DELETE` statements only contain primary keys. All other data fields are unset.

## Current Support

* [Postgres](../integrations/sources/postgres.md) \(For a quick video overview of CDC on Postgres, click [here](https://www.youtube.com/watch?v=NMODvLgZvuE&ab_channel=Airbyte)\)
* [MySQL](../integrations/sources/mysql.md)
* [Microsoft SQL Server / MSSQL](../integrations/sources/mssql.md)

## Coming Soon

* Oracle DB
* Please [create a ticket](https://github.com/airbytehq/airbyte/issues/new/choose) if you need CDC support on another database!

## Additional information

* [An overview of Airbyte’s replication modes](https://airbyte.com/blog/understanding-data-replication-modes).
* [Understanding Change Data Capture (CDC): Definition, Methods and Benefits](https://airbyte.com/blog/change-data-capture-definition-methods-and-benefits)
* [Explore Airbyte's Change Data Capture (CDC) synchronization](https://airbyte.com/tutorials/incremental-change-data-capture-cdc-replication)

