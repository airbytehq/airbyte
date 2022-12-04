# Cassandra Destination

Cassandra is a free and open-source, distributed, wide-column store, NoSQL database management system designed to handle
large amounts of data across many commodity servers, providing high availability with no single point of failure

The data is structured in keyspaces and tables and is partitioned and replicated across different nodes in the
cluster.  
[Read more about Cassandra](https://cassandra.apache.org/_/index.html)

This connector maps an incoming `stream` to a Cassandra `table` and a `namespace` to a Cassandra`keyspace`.  
When using destination sync mode `append` and `append_dedup`, an `insert` operation is performed against an existing
Cassandra table.  
When using `overwrite`, the records are first placed in a temp table. When all the messages have been received the data
is copied to the final table which is first truncated and the temp table is deleted.

The Implementation uses the [Datastax](https://github.com/datastax/java-driver) driver in order to access
Cassandra. [CassandraCqlProvider](./src/main/java/io/airbyte/integrations/destination/cassandra/CassandraCqlProvider.java)
handles the communication with the Cassandra cluster and internally it uses
the [SessionManager](./src/main/java/io/airbyte/integrations/destination/cassandra/SessionManager.java) to retrieve a
CqlSession to the cluster.

The [CassandraMessageConsumer](./src/main/java/io/airbyte/integrations/destination/cassandra/CassandraMessageConsumer.java)
class contains the logic for handling airbyte messages, events and copying data between tables.

## Development

See the [CassandraCqlProvider](./src/main/java/io/airbyte/integrations/destination/cassandra/CassandraCqlProvider.java)
class on how to use the datastax driver.

[Datastax docs.](https://docs.datastax.com/en/developer/java-driver/3.0/)