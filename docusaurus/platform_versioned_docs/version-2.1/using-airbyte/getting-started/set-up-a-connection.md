---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";
import DocCardList from '@theme/DocCardList';

# Connections and streams

A **connection** is the relationship between a source connector and a destination connector. When you create a connection, you create an automated data pipeline that syncs data from a source to a destination. Connections define things like:

- What data Airbyte should replicate
- How Airbyte should read and write data
- When Airbyte should initiate a data sync
- Where Airbyte should write replicated data
- How Airbyte should handle schema drift

Each iteration of a connection is called a **sync**. In most cases, you run syncs on an automated schedule, but you can also run them manually.

A **stream** is a group of related records within a connection. Depending on the destination, a stream might be a table, file, multiple files, or blob. Airbyte uses the term `stream` to generalize the flow of data to destinations of all types and formats. You can configure each stream if you need granular control over specifics parts of your data. Examples of streams are:

- A table in a relational database
- A resource or API endpoint for a REST API
- The records from a directory containing files in a filesystem

<DocCardList/>
