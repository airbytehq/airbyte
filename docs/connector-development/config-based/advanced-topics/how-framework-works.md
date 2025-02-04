# How the Framework Works

1. Given the connection config and an optional stream state, the `PartitionRouter` computes the partitions that should be routed to read data.
2. Iterate over all the partitions defined by the stream's partition router.
3. For each partition,
   1. Submit a request to the partner API as defined by the requester
   2. Select the records from the response
   3. Repeat for as long as the paginator points to a next page

[connector-flow](../assets/connector-flow.png)