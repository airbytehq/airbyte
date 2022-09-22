# Connections and Sync Modes

A connection is a configuration for syncing data between a source and a destination. To setup a connection, a user must configure things such as:

* Sync schedule: when to trigger a sync of the data.
* Destination [Namespace](../namespaces.md) and stream names: where the data will end up being written.
* A catalog selection: which [streams and fields](../airbyte-protocol.md#catalog) to replicate from the source
* Sync mode: how streams should be replicated \(read and write\):
* Optional transformations: how to convert Airbyte protocol messages \(raw JSON blob\) data into some other data representations. 

## Sync schedules

Sync schedules are explained below. For information about catalog selections, see [AirbyteCatalog & ConfiguredAirbyteCatalog](../airbyte-protocol.md#catalog).

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

## Destination namespace

The location of where a connection replication will store data is referenced as the destination namespace. The destination connectors should create and write records \(for both raw and normalized tables\) in the specified namespace which should be configurable in the UI via the Namespace Configuration field \(or NamespaceDefinition in the API\). You can read more about configuring namespaces [here](../namespaces.md).

## Destination stream name

### Prefix stream name

Stream names refer to table names in a typical RDBMS. But it can also be the name of an API endpoint, etc. Similarly to the namespace, stream names can be configured to diverge from their names in the source with a "prefix" field. The prefix is prepended to the source stream name in the destination.

## Stream-specific customization

All the customization of namespace and stream names described above will be equally applied to all streams selected for replication in a catalog per connection. If you need more granular customization, stream by stream, for example, or with different logic rules, then you could follow the tutorial on [customizing transformations with dbt](../../operator-guides/transformation-and-normalization/transformations-with-dbt.md).

## Sync modes

A sync mode governs how Airbyte reads from a source and writes to a destination. Airbyte provides different sync modes to account for various use cases. To minimize confusion, a mode's behavior is reflected in its name. The easiest way to understand Airbyte's sync modes is to understand how the modes are named.

1. The first part of the name denotes how the source connector reads data from the source:
   1. Incremental: Read records added to the source since the last sync job. \(The first sync using Incremental is equivalent to a Full Refresh\)
      * Method 1: Using a cursor. Generally supported by all connectors whose data source allows extracting records incrementally.
      * Method 2: Using change data capture. Only supported by some sources. See [CDC](../cdc.md) for more info.
   2. Full Refresh: Read everything in the source.
2. The second part of the sync mode name denotes how the destination connector writes data. This is not affected by how the source connector produced the data:
   1. Overwrite: Overwrite by first deleting existing data in the destination.
   2. Append: Write by adding data to existing tables in the destination.
   3. Deduped History: Write by first adding data to existing tables in the destination to keep a history of changes. The final table is produced by de-duplicating the intermediate ones using a primary key.

A sync mode is therefore, a combination of a source and destination mode together. The UI exposes the following options, whenever both source and destination connectors are capable to support it for the corresponding stream:

* [Full Refresh Overwrite](full-refresh-overwrite.md): Sync the whole stream and replace data in destination by overwriting it.
* [Full Refresh Append](full-refresh-append.md): Sync the whole stream and append data in destination.
* [Incremental Append](incremental-append.md): Sync new records from stream and append data in destination.
* [Incremental Deduped History](incremental-deduped-history.md): Sync new records from stream and append data in destination, also provides a de-duplicated view mirroring the state of the stream in the source.

## Optional operations

### Airbyte basic normalization

As described by the [Airbyte Protocol from the Airbyte Specifications](../airbyte-protocol.md), a replication is composed of source connectors that are transmitting data in a JSON format. It is then written as such by the destination connectors.

On top of this replication, Airbyte provides the option to enable or disable an additional transformation step at the end of the sync called [basic normalization](../basic-normalization.md). This operation is:

* only available for destinations that support dbt execution.
* responsible for automatically generating a pipeline or a DAG of dbt transformation models to convert JSON blob objects into normalized tables.
* responsible for running and applying these dbt models to the data written in the destination.

### Custom sync operations

Further operations can be included in a sync on top of Airbyte basic normalization \(or even to replace it completely\). See [operations](../operations.md) for more details.

