# Scylla

## Sync overview

### Output schema

The incoming airbyte data is structured in keyspaces and tables and is partitioned and replicated across different nodes
in the cluster. This connector maps an incoming `stream` to a Scylla `table` and a `namespace` to a Scylla`keyspace`.
Fields in the airbyte message become different columns in the Scylla tables.

### Data type mapping

This section should contain a table mapping each of the connector's data types to Airbyte types. At the moment, Airbyte
uses the same types used by [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html)
. `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number` are the most commonly used data types.

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |

### Features

This section should contain a table with the following format:

| Feature | Supported?(Yes/No) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Replicate Incremental Deletes | No |  |
| For databases, WAL/Logical replication |  |  |
| SSL connection |  |  |
| SSH Tunnel Support |  |  |
| (Any other source-specific features) |  |  |

### Performance considerations

Scylla is highly performant and is designed to handle large amounts of data by using different nodes in the cluster in
order to perform write operations. As long as you have enough nodes in your cluster the database can scale infinitely
and handle any amount of data from the connector.

## Getting started

### Requirements

* What versions of this connector does this implementation support? (e.g: `postgres v3.14 and above`)
* Configuration
    * Keyspace [default keyspace]
    * Username [authentication username]
    * Password [authentication password]
    * Address [cluster address]
    * Port [default: 9042]
    * Replication [optional] [default: 1]
* Network accessibility requirements ?
* Username:Password authentication is supported.

### Setup guide

For each of the above high-level requirements as appropriate, add or point to a follow-along guide. See existing source
or destination guides for an example.

For each major cloud provider we support, also add a follow-along guide for setting up Airbyte to connect to that
destination. See the Postgres destination guide for an example of what this should look like.