# Scylla Destination

Scylla is an open-source distributed NoSQL wide-column data store designed to handle large amounts of data across many
commodity servers, providing high availability with no single point of failure. It is designed to be compatible with
Apache Cassandra while achieving significantly higher throughputs and lower latencies. It supports the same protocols as
Cassandra (CQL and Thrift) and the same file formats (SSTable)

The data is structured in keyspaces and tables and is partitioned and replicated across different nodes in the
cluster.  
[Read more about Scylla](https://www.scylladb.com/)

This connector maps an incoming `stream` to a Scylla `table` and a `namespace` to a Scylla`keyspace`.  
When using destination sync mode `append` and `append_dedup`, an `insert` operation is performed against an existing
Scylla table.  
When using `overwrite`, the records are first placed in a temp table. When all the messages have been received the data
is copied to the final table which is first truncated and the temp table is deleted.

The Implementation uses the [Scylla](https://github.com/scylladb/java-driver/) driver in order to access
Scylla. [ScyllaCqlProvider](./src/main/java/io/airbyte/integrations/destination/scylla/ScyllaCqlProvider.java)
handles the communication with the Scylla cluster and internally it uses
the [ScyllaSessionPool](./src/main/java/io/airbyte/integrations/destination/scylla/ScyllaSessionPool.java) to retrieve a
session to the cluster.

The [ScyllaMessageConsumer](./src/main/java/io/airbyte/integrations/destination/scylla/ScyllaMessageConsumer.java)
class contains the logic for handling airbyte messages, events and copying data between tables.

## Development

See the [ScyllaCqlProvider](./src/main/java/io/airbyte/integrations/destination/scylla/ScyllaCqlProvider.java)
class on how to use the Scylla driver.

[Scylla driver docs.](https://docs.scylladb.com/using-scylla/drivers/cql-drivers/scylla-java-driver/)