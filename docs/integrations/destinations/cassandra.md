# Cassandra

## Prerequisites
- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Cassandra connector to version `0.1.3` or newer


## Sync overview

### Output schema

The incoming airbyte data is structured in keyspaces and tables and is partitioned and replicated across different nodes
in the cluster. This connector maps an incoming `stream` to a Cassandra `table` and a `namespace` to a
Cassandra`keyspace`. Fields in the airbyte message become different columns in the Cassandra tables. Each table will 
contain the following columns.

* `_airbyte_ab_id`: A random uuid generator to be used as a partition key.
* `_airbyte_emitted_at`: a timestamp representing when the event was received from the data source.
* `_airbyte_data`: a json text representing the extracted data.

### Features

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured DynamoDB table. |
| Incremental - Append Sync | ✅ |  |
| Incremental - Deduped History | ❌ | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | ✅ | Namespace will be used as part of the table name. |



### Performance considerations

Cassandra is designed to handle large amounts of data by using different nodes in the cluster in order to perform write
operations. As long as you have enough nodes in the cluster the database can scale infinitely and handle any amount of
data from the connector.

## Getting started

### Requirements

* The driver is compatible with _Cassandra >= 2.1_
* Configuration
    * Keyspace [default keyspace to use when writing data]
    * Username [authentication username]
    * Password [authentication password]
    * Address [cluster address]
    * Port [default: 9042]
    * Datacenter [optional] [default: datacenter1]
    * Replication [optional] [default: 1]
    
### Setup guide

######TODO: more info, screenshots?, etc...
