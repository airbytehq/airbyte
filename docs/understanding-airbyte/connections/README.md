# Connections

A connection is a configuration for syncing data between a source and a destination. To setup a connection, a user must configure things such as:

* A catalog selection: which [streams and fields](../catalog.md) to replicate from the source
* Sync mode: how streams should be replicated (read and write):
* Sync schedule: when to trigger a sync of the data
* Optional transformations: how to convert Airbyte protocol messages (raw JSON blob) data into some other data representations. 

## Sync modes

Note that Sync mode names are generally composed of two parts on purpose. This is because Source and Destination connectors are decoupled from each other.
One is responsible for reading, and the other for writing.

1. The first part of the sync mode name denotes how source connectors work:
  
  * Incremental: Read only the last records in the source since last read operation during a previous sync
      * Method 1: comparing to a cursor value
      * Method 2: using [CDC](../cdc.md), only available for certain limited number of sources that can support it.
  * Full Refresh: Read everything in the source

2. The second part of the sync mode name denotes how destination connectors work, regardless of how the source is producing data:

  * Overwrite: Delete and then write over data in the destination that already exists
  * Append: Write by adding data to existing tables in the destination
  * Deduped History: Write by adding data to existing tables in the destination to keep a history of changes. The final table is produced by deduplicating the intermediate ones using a primary key.

A sync mode is therefore, a combination of a source and destination mode together. The UI exposes the following options, whenever both source and destination connectors are capable to support it for the corresponding stream:
* [Full Refresh Overwrite](full-refresh-overwrite.md): Sync the whole stream and replace data in destination by overwriting it.
* [Full Refresh Append](full-refresh-append.md): Sync the whole stream and append data in destination.
* [Incremental Append](incremental-append.md): Sync new records from stream and append data in destination.
* [Incremental Deduped History](incremental-deduped-history.md): Sync new records from stream and append data in destination, also provides a de-duplicated view mirroring the state of the stream in the source.

## Sync schedules

Sync schedules are explained below. For information about catalog selections, see [AirbyteCatalog & ConfiguredAirbyteCatalog](../catalog.md).

Syncs will be triggered by either:

* A manual request \(i.e: clicking the "Sync Now" button in the UI\)
* A schedule

When a scheduled connection is first created, a sync is executed as soon as possible. After that, a sync is run once the time since the last sync \(whether it was triggered manually or due to a schedule\) has exceeded the schedule interval. For example, consider the following illustrative scenario:

* **October 1st, 2pm**, a user sets up a connection to sync data every 24 hours. 
* **October 1st, 2:01pm**: sync job runs 
* **October 2nd, 2:01pm:** 24 hours have passed since the last sync, so a sync is triggered. 
* **October 2nd, 5pm**: The user manually triggers a sync from the UI
* **October 3rd, 2:01pm:** since the last sync was less than 24 hours ago, no sync is run
* **October 3rd, 5:01pm:** It has been more than 24 hours since the last sync, so a sync is run

## Optional operations

### Airbyte basic normalization

As described by the [Airbyte Protocol from the Airbyte Specifications](../airbyte-specification.md), a replication is composed of source connectors that are transmitting data in a JSON format. It is then written as such by the destination connectors. 

On top of this replication, Airbyte provides the option to enable or disable an additional transformation step at the end of the sync called [basic normalization](../basic-normalization.md). This operation is:

- only available for destinations that supports dbt execution.
- responsible for automatically generating a pipeline or a DAG of dbt transformation models to convert JSON blob objects into normalized tables.
- running and applying these dbt models to the data written in the destination.

### Custom sync operations

Further operations can be included in a sync on top of Airbyte basic normalization (or even to replace it completely). Potential applications are:

- Customized normalization to better fit the requirements of your own business context.
- Business transformations from a technical data representation into a more logical and business oriented data structure. This can facilitate usage by end-users, non-technical, executives for Business Intelligence dashboard and report.
- Data Quality, performance optimization, alerting and monitoring etc
- Integration with other tools from your data stack (orchestration, data visualization, etc)

See [operations](../operations.md) for more details.
