---
products: all
---

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

| Concept                                                                                                         | Description                                                        |
|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| [Replication Frequency](/using-airbyte/core-concepts/sync-schedules.md)                                         | When should a data sync be triggered?                              | 
| [Destination Namespace and Stream Prefix](/using-airbyte/core-concepts/namespaces.md)                           | Where should the replicated data be written?                       | 
| [Sync Mode](/using-airbyte/core-concepts/sync-modes/README.md)                                                  | How should the streams be replicated (read and written)?           | 
| [Schema Propagation](/cloud/managing-airbyte-cloud/manage-schema-changes.md)                                    | How should Airbyte handle schema drift in sources?                 | 
| [Catalog Selection](/cloud/managing-airbyte-cloud/configuring-connections.md#modify-streams-in-your-connection) | What data should be replicated from the source to the destination? | 

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

## Sync Schedules

There are three options for scheduling a sync to run: 
- Scheduled (ie. every 24 hours, every 2 hours)
- [CRON schedule](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html)
- Manual \(i.e: clicking the "Sync Now" button in the UI or through the API\)

For more details, see our [Sync Schedules documentation](sync-schedules.md).

## Destination Namespace

A namespace defines where the data will be written to your destination. You can use the namespace to group streams in a source or destination. In a relational database system, this is typically known as a schema.

For more details, see our [Namespace documentation](namespaces.md).

## Sync Mode

A sync mode governs how Airbyte reads from a source and writes to a destination. Airbyte provides different sync modes depending on what you want to accomplish.

Read more about each [sync mode](using-airbyte/core-concepts/sync-modes) and how they differ. 

## Typing and Deduping

Typing and deduping ensures the data emitted from sources is written into the correct type-cast relational columns and only contains unique records. Typing and deduping is only relevant for the following relational database & warehouse destinations:

- Snowflake
- BigQuery

:::info
Typing and Deduping is the default method of transforming datasets within data warehouse and database destinations after they've been replicated. We are retaining documentation about normalization to support legacy destinations. 
:::

For more details, see our [Typing & Deduping documentation](/using-airbyte/core-concepts/typing-deduping).

## Basic Normalization

Basic Normalization transforms data after a sync to denest columns into their own tables. Note that normalization is only available for the following relational database & warehouse destinations:

- Redshift
- Postgres
- Oracle
- MySQL
- MSSQL

For more details, see our [Basic Normalization documentation](/using-airbyte/core-concepts/basic-normalization.md).

## Custom Transformations

Airbyte integrates natively with dbt to allow you to use dbt for post-sync transformations. This is useful if you would like to trigger dbt models after a sync successfully completes.

For more details, see our [dbt integration documentation](/cloud/managing-airbyte-cloud/dbt-cloud-integration.md). 

## Workspace

A workspace is a grouping of sources, destinations, connections, and other configurations. It lets you collaborate with team members and share resources across your team under a shared billing account.

## Glossary of Terms

You can find a extended list of [Airbyte specific terms](https://glossary.airbyte.com/term/airbyte-glossary-of-terms/), [data engineering concepts](https://glossary.airbyte.com/term/data-engineering-concepts) or many [other data related terms](https://glossary.airbyte.com/).
