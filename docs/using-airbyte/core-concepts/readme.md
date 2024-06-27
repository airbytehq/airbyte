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

| Concept                                                                                                                  | Description                                                        |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| [Stream and Field Selection](/cloud/managing-airbyte-cloud/configuring-connections.md#modify-streams-in-your-connection) | What data should be replicated from the source to the destination? |
| [Sync Mode](/using-airbyte/core-concepts/sync-modes/README.md)                                                           | How should the streams be replicated (read and written)?           |
| [Sync Schedule](/using-airbyte/core-concepts/sync-schedules.md)                                                          | When should a data sync be triggered?                              |
| [Destination Namespace and Stream Prefix](/using-airbyte/core-concepts/namespaces.md)                                    | Where should the replicated data be written?                       |
| [Schema Propagation](using-airbyte/schema-change-management.md)                                                          | How should Airbyte handle schema drift in sources?                 |

## Stream

A stream is a group of related records. Depending on the destination, it may be called a table, file, or blob. We use the term `stream` to generalize the flow of data to various destinations.

Examples of streams:

- A table in a relational database
- A resource or API endpoint for a REST API
- The records from a directory containing many files in a filesystem

## Record

A record is a single entry or unit of data. This is commonly known as a "row". A record is usually unique and contains information related to a particular entity, like a customer or transaction.

Examples of records:

- A row in the table in a relational database
- A line in a file
- A unit of data returned from an API

## Field

A field is an attribute of a record in a stream.

Examples of fields:

- A column in the table in a relational database
- A field in an API response

## Sync Schedule

There are three options for scheduling a sync to run:

- Scheduled (ie. every 24 hours, every 2 hours)
- [CRON schedule](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html)
- Manual \(i.e: clicking the "Sync Now" button in the UI or through the API\)

For more details, see our [Sync Schedules documentation](sync-schedules.md).

## Destination Namespace

A namespace defines where the data will be written to your destination. You can use the namespace to group streams in a source or destination. In a relational database system, this is typically known as a schema.

Depending on your destination, you may know this more commonly as the "Dataset", "Schema" or "Bucket Path". The term "Namespace" is used to generalize the concept across various destinations.

For more details, see our [Namespace documentation](namespaces.md).

## Sync Mode

A sync mode governs how Airbyte reads from a source and writes to a destination. Airbyte provides several sync modes depending what you want to accomplish. The sync modes define how your data will sync and whether duplicates will exist in the dstination.

Read more about each [sync mode](/using-airbyte/core-concepts/sync-modes/README.md) and how they differ.

## Typing and Deduping

Typing and deduping ensures the data emitted from sources is written into the correct type-cast relational columns, and if deduplication is selected, only contains unique records. Typing and deduping is only relevant for relational database & warehouse destinations. For more details, see our [Typing & Deduping documentation](/using-airbyte/core-concepts/typing-deduping).

## Custom Transformations

Airbyte Cloud integrates natively with dbt to allow you to use dbt for post-sync transformations. This is useful if you would like to trigger dbt models after a sync successfully completes.

Custom transformation is not available for Airbyte Open-Source.

## Workspace

A workspace is a grouping of sources, destinations, connections, and other configurations. It lets you collaborate with team members and share resources across your team under a shared billing account.

## Organization

Organizations let you collaborate with team members and share workspaces across your team.

## Glossary of Terms

You can find a extended list of [Airbyte specific terms](https://glossary.airbyte.com/term/airbyte-glossary-of-terms/), [data engineering concepts](https://glossary.airbyte.com/term/data-engineering-concepts) or many [other data related terms](https://glossary.airbyte.com/).
