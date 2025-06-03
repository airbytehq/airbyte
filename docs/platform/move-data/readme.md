---
products: all
---

import DocCardList from '@theme/DocCardList';

# Move data

In Airbyte, you move data from **sources** to **destinations** using **connectors**. These connectors form **connections**, which contain **streams** of data.

This section explains these critical concepts and shows you how to move data in Airbyte.

## Sources and destinations

A **source** is the database, API, or other system **from** which you sync data. A **destination** is the data warehouse, data lake, database, or other system **to** which you sync data.

## Connectors

A **connector** is the component Airbyte uses to connect to and interact with your source or destination. Connectors are a key difference between a resilient Airbyte deployment and a more brittle in-house data pipeline.

Airbyte has two types of connectors: source connectors and destination connectors. Sometimes, people abbreviate these to "sources" and "destinations." That can be a little confusing, so to be clear, a connector isn't the same thing as the source or destination it connects to, but it's closely related to them.

Connectors have [different support levels](/integrations/connector-support-levels).

### Connectors are open source

Airbyte provides over 600 connectors, almost all of which are open source. You can contribute to connectors to make them better or keep them up-to-date as third-parties make changes, or fork it to make it more suitable to your particular needs. 

If you don't see the connector you need, you can build one from scratch. Airbyte provides a no-code and low-code Connector Builder as well as Connector Development Kits (CDKs), which are more traditional software development tools.

## Connections and streams

When you combine a source connector and a destination connector, you get a **connection**. A connection is the automated data pipeline that replicates data from a source to a destination. Connections define things like:

- What data Airbyte should replicate

- How Airbyte should read and write data

- When Airbyte should initiate a data sync

- Where Airbyte should write replicated data

- How Airbyte should handle schema drift

A **stream** is a group of related records within a connection. Depending on the destination, a stream might be a table, file, or blob. Airbyte uses the term `stream` to generalize the flow of data to destinations of all types and formats. Examples of streams:

- A table in a relational database

- A resource or API endpoint for a REST API

- The records from a directory containing many files in a filesystem

## Data activation and reverse-ETL

The ELT process is biased to consolidation. This work features movement from many databases and APIs into data warehouses and data lakes. This type of work is designed to power use cases like internal reporting, analytics, and more recently, AI.

However, Airbyte also works the other way: moving consolidated data out of data warehouses and back into the operational systems teams rely on. This effort is often called reverse-ETL or data activation. This process turns raw data into actionable, valuable insights by moving it to the higher-context systems where it can empower day-to-day work.

### An example of data activation with Airbyte

Imagine you want to give your sales team the maximum amount of context and knowledge possible. Your CRM, Salesforce, has a lot in it, but much of this information is manually entered by your sales reps based on customer calls and research.

You have a data warehouse filled with data you've synced from dozens or hundreds of other data sources.

You decide to make Salesforce more powerful by populating it with things like past customer behavior, how they engage with your marketing campaigns, past support experiences, etc. You sync this data automatically and regularly to keep it fresh based on the latest data in your sources.

This type of data gives your front-line customer-facing teams powerful insight about what their customers need, what they're struggling with, and what opportunities exist to improve customer satisfaction, land new accounts, and expand existing ones.

## Start moving data

<DocCardList />
