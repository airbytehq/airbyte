# Namespaces

## What is a Namespace?

Technical systems often group their underlying data into namespaces with each namespace's data isolated from another namespace. This isolation allows for better organisation and flexibility, leading to better usability.

An example of a namespace is the RDMS's `schema` concept. Some common use cases for schemas are enforcing permissions, segregating test and production data and general data organisation.

## Syncing

The Airbyte Protocol supports namespaces and allows Sources to define namespaces, and Destinations to write to various namespaces.

The most common use of namespaces is in the context of database sources and destinations. For databases, generally, a namespace is synonymous with a schema. In the Postgres source, for example, the table `public.users` would be represented in Airbyte as `{ "namespace": "public", "name" "users" }`. If replicating this into a destination that supports namespacing, by default, records from this table would be replicated into `public.users` in the destination.

If a sync is conducted with a Source and Destination that both support namespaces, the source-defined namespace will be the schema in the Destination into which the data is replicated. For such syncs, data is replicated into the Destination in a layout matching the Source.

All of this is automatic, and requires no additional user configuration.

If the Source does not support namespaces, the data will be replicated into the Destination's default namespace. For databases, the default namespace is the schema provided in the destination configuration.

If the Destination does not support namespaces, the [namespace field](https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L64) is ignored.

The following table summarises how this works. We assume the Source contains a data source named `cake`.

| Source supports Namespaces | Destination supports Namespaces | Source-defined Namespace | Default Destination Namespace | Final Destination Namespace | Airbyte Stream Name | Example \(fully-qualified Source path -&gt; fully-qualified Destination path\) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Yes | Yes | `lava` | `chocolate` | `lava` | `cake` | `lava.cake` -&gt; `lava.cake` |
| Yes | No | `lava` | `chocolate` | `chocolate` | `cake` | `lava.cake` -&gt; `chocolate.cake` |
| No | Yes | `None` | `chocolate` | `chocolate` | `cake` | `lava.cake` -&gt; `chocolate.cake` |

## Requirements

* Both Source and Destination connectors need to support namespaces.
* Relevant Source and Destination connectors need to be at least version `0.3.0` or later.
* Airbyte version `0.21.0-alpha` or later.

## Current Support

### Sources

* MSSQL
* MYSQL
* Oracle DB
* Postgres
* Redshift

### Destination

* BigQuery
* Postgres
* Snowflake
* Redshift

## Coming Soon

* Ability to prefix namespaces.
* Ability to configure custom namespaces.
* Ability to toggle the namespaces functionality.
* Please [create a ticket](https://github.com/airbytehq/airbyte/issues/new/choose) if other namespace features come to mind!

We welcome you to join our [Slack](https://airbyte.io/community/) if you have any other questions!

