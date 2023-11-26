# Core Concepts

Airbyte enables you to build data pipelines and replicate data from a source to a destination. You can configure how frequently the data is synced, what data is replicated, and how the data is written to in the destination.

This page describes the concepts you need to know to use Airbyte.

## Source

A source is an API, file, database, or data warehouse that you want to ingest data from.

## Destination

A destination is a data warehouse, data lake, database, or an analytics tool where you want to load your ingested data.

## Connector

An Airbyte component which pulls data from a source or pushes data to a destination.

## Connection

A connection is an automated data pipeline that replicates data from a source to a destination. Setting up a connection enables configuration of the following parameters:

| Concept              | Description                                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------------------------------|
| Replication Frequency | When should a data sync be triggered? | 
| Destination Namespace and Stream Prefix | Where should the replicated data be written? | 
| Catalog Selection | What data (streams and columns) should be replicated from the source to the destination? | 
| Sync Mode | How should the streams be replicated (read and written)? | 
| Schema Propagation | How should Airbyte handle schema drift in sources? | 
## Stream

A stream is a group of related records.

Examples of streams:

- A table in a relational database
- A resource or API endpoint for a REST API
- The records from a directory containing many files in a filesystem

## Field

A field is an attribute of a record in a stream.

Examples of fields:

- A column in the table in a relational database
- A field in an API response

## Sync schedules

Syncs will be triggered by either:

- A manual request \(i.e: clicking the "Sync Now" button in the UI or through the API\)
- A schedule
- CRON schedule

When a scheduled connection is first created, a sync is executed as soon as possible. After that, a sync is run once the time since the last sync \(whether it was triggered manually or due to a schedule\) has exceeded the schedule interval. For example, consider the following illustrative scenario:

- **October 1st, 2pm**, a user sets up a connection to sync data every 24 hours.
- **October 1st, 2:01pm**: sync job runs
- **October 2nd, 2:01pm:** 24 hours have passed since the last sync, so a sync is triggered.
- **October 2nd, 5pm**: The user manually triggers a sync from the UI
- **October 3rd, 2:01pm:** since the last sync was less than 24 hours ago, no sync is run
- **October 3rd, 5:01pm:** It has been more than 24 hours since the last sync, so a sync is run

## Namespace

Namespace is a method of grouping streams in a source or destination. Namespaces are used to generally organize data, segregate tests and production data, and enforce permissions. In a relational database system, this is known as a schema.

In a source, the namespace is the location from where the data is replicated to the destination. In a destination, the namespace is the location where the replicated data is stored in the destination. 

Airbyte supports the following configuration options for a connection:

   | Destination Namepsace | Description                |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Destination default | All streams will be replicated to the single default namespace defined by the Destination. |
| Mirror source structure | Some sources (for example, databases) provide namespace information for a stream. If a source provides namespace information, the destination will mirror the same namespace when this configuration is set. For sources or streams where the source namespace is not known, the behavior will default to the "Destination default" option.  |
| Custom format | All streams will be replicated to a single user-defined namespace. |

For more details, see our [Namespace documentation](namespaces.md).

## Connection sync modes

A sync mode governs how Airbyte reads from a source and writes to a destination. Airbyte provides different sync modes to account for various use cases.

- **Full Refresh | Overwrite:** Sync all records from the source and replace data in destination by overwriting it each time.
- **Full Refresh | Append:** Sync all records from the source and add them to the destination without deleting any data. This creates a historical copy of all records each sync.
- **Incremental Sync | Append:** Sync new records from the source and add them to the destination without deleting any data. This enables efficient historical tracking over time of data. 
- **Incremental Sync | Append + Deduped:** Sync new records from the source and add them to the destination. Also provides a de-duplicated view mirroring the state of the stream in the source. This is the most common replication use case. 

Read more about each [sync mode](using-airbyte/core-concepts/sync-modes) and how they differ. 

## Normalization

Normalization is the process of structuring data from the source into a format appropriate for consumption in the destination. For example, when writing data from a nested, dynamically typed source like a JSON API to a relational destination like Postgres, normalization is the process which un-nests JSON from the source into a relational table format which uses the appropriate column types in the destination.

Note that normalization is only relevant for the following relational database & warehouse destinations:

- Redshift
- Postgres
- Oracle
- MySQL
- MSSQL

Other destinations do not support normalization as described in this section, though they may normalize data in a format that makes sense for them. For example, the S3 destination connector offers the option of writing JSON files in S3, but also offers the option of writing statically typed files such as Parquet or Avro.

After a sync is complete, Airbyte normalizes the data. When setting up a connection, you can choose one of the following normalization options:

- Raw data (no normalization): Airbyte places the JSON blob version of your data in a table called `_airbyte_raw_<stream name>`
- Basic Normalization: Airbyte converts the raw JSON blob version of your data to the format of your destination. _Note: Not all destinations support normalization._
- [dbt Cloud integration](https://docs.airbyte.com/cloud/managing-airbyte-cloud/dbt-cloud-integration): Airbyte's dbt Cloud integration allows you to use dbt Cloud for transforming and cleaning your data during the normalization process.

:::note

Normalizing data may cause an increase in your destination's compute cost. This cost will vary depending on the amount of data that is normalized and is not related to Airbyte credit usage.

:::

### Typing and Deduping

As described by the [Airbyte Protocol from the Airbyte Specifications](/understanding-airbyte/airbyte-protocol.md), replication is composed of source connectors that are transmitting data in a JSON format. It is then written as such by the destination connectors. On top of this replication, Airbyte's database and datawarehous destinations can provide converstions from the raw JSON data into type-cast relational columns. Learn more [here](/understanding-airbyte/typing-deduping).

Note that typing and deduping is only relevant for the following relational database & warehouse destinations:

- Snowflake
- BigQuery

:::note

Typing and Deduping may cause an increase in your destination's compute cost. This cost will vary depending on the amount of data that is transformed and is not related to Airbyte credit usage.

:::

## Workspace

A workspace is a grouping of sources, destinations, connections, and other configurations. It lets you collaborate with team members and share resources across your team under a shared billing account.

When you [sign up](http://cloud.airbyte.com/signup) for Airbyte Cloud, we automatically create your first workspace where you are the only user with access. You can set up your sources and destinations to start syncing data and invite other users to join your workspace.

## Glossary of Terms

You find and extended list of [Airbyte specific terms](https://glossary.airbyte.com/term/airbyte-glossary-of-terms/), [data engineering concepts](https://glossary.airbyte.com/term/data-engineering-concepts) or many [other data related terms](https://glossary.airbyte.com/).
