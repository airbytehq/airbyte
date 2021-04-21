# Namespaces

## What is a Namespace?
Technical systems often group their underlying data into namespaces with each namespace's data isolated from another namespace. This isolation allow
for better organisation and flexibility, leading to better usability.

An example of namespace is a RDMS's `schema` concept. Some common use cases for schemas are enforcing permissiong, segregating test and production data
and general data organisation.

## Syncing
The Airbyte protocol supports namespaces and allows Sources to define namespaces, and Destinations to write to a various namespaces.

A sync conducted with a Source and Destination that both support namespaces, the source-defined namespace will be the schema in the Destination into which the data is replicated. For such syncs,
data is replicated into the Destination in a layout matching the Source.

All of this is automatic, and requires no additional user configuration.

If the Source does not support namespaces, the data will be replicated into the Destination's default namespace.

If the Destination does not support namespaces, the [namespace field](https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L64) is ignored.

## Requirements
* Both Source and Destiation connectors need to support namespaces.
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
* Ability to toggle namespaces.
* Please [create a ticket](https://github.com/airbytehq/airbyte/issues/new/choose) if other namespace features come to mind!

We welcome you to join our [Slack](https://airbyte.io/community/) if you have any other questions!
