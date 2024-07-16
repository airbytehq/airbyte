# Troubleshooting Mongo DB Sources

## Connector Limitations

### MongoDB Oplog and Change Streams

[MongoDB's Change Streams](https://www.mongodb.com/docs/manual/changeStreams/) are based on the [Replica Set Oplog](https://www.mongodb.com/docs/manual/core/replica-set-oplog/). This has retention limitations. Syncs that run less frequently than the retention period of the Oplog may encounter issues with missing data.

We recommend adjusting the Oplog size for your MongoDB cluster to ensure it holds at least 24 hours of changes. For optimal results, we suggest expanding it to maintain a week's worth of data. To adjust your Oplog size, see the corresponding tutorials for [MongoDB Atlas](https://www.mongodb.com/docs/atlas/cluster-additional-settings/#set-oplog-size) (fully-managed) and [MongoDB shell](https://www.mongodb.com/docs/manual/tutorial/change-oplog-size/) (self-hosted).

If you are running into an issue similar to "invalid resume token", it may mean you need to:

1. Increase the Oplog retention period.
2. Increase the Oplog size.
3. Increase the Airbyte sync frequency.

You can run the commands outlined [in this tutorial](https://www.mongodb.com/docs/manual/tutorial/troubleshoot-replica-sets/#check-the-size-of-the-oplog) to verify the current of your Oplog. The expect output is:

```yaml
configured oplog size: 10.10546875MB
log length start to end: 94400 (26.22hrs)
oplog first event time: Mon Mar 19 2012 13:50:38 GMT-0400 (EDT)
oplog last event time: Wed Oct 03 2012 14:59:10 GMT-0400 (EDT)
now: Wed Oct 03 2012 15:00:21 GMT-0400 (EDT)
```

When importing a large MongoDB collection for the first time, the import duration might exceed the Oplog retention period. The Oplog is crucial for incremental updates, and an invalid resume token will require the MongoDB collection to be re-imported to ensure no source updates were missed.

### Supported MongoDB Clusters

- Only supports [replica set](https://www.mongodb.com/docs/manual/replication/) cluster type.
- TLS/SSL is required by this connector. TLS/SSL is enabled by default for MongoDB Atlas clusters. To enable TSL/SSL connection for a self-hosted MongoDB instance, please refer to [MongoDb Documentation](https://docs.mongodb.com/manual/tutorial/configure-ssl/).
- Views, capped collections and clustered collections are not supported.
- Empty collections are excluded from schema discovery.
- Collections with different data types for the values in the `_id` field among the documents in a collection are not supported. All `_id` values within the collection must be the same data type.
- Atlas DB cluster are only supported in a dedicated M10 tier and above. Lower tiers may fail during connection setup.

### Schema Discovery & Enforcement

- Schema discovery uses [sampling](https://www.mongodb.com/docs/manual/reference/operator/aggregation/sample/) of the documents to collect all distinct top-level fields. This value is universally applied to all collections discovered in the target database. The approach is modelled after [MongoDB Compass sampling](https://www.mongodb.com/docs/compass/current/sampling/) and is used for efficiency. By default, 10,000 documents are sampled. This value can be increased up to 100,000 documents to increase the likelihood that all fields will be discovered. However, the trade-off is time, as a higher value will take the process longer to sample the collection.
- When Running with Schema Enforced set to `false` there is no attempt to discover any schema. See more in [Schema Enforcement](#Schema-Enforcement).

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or
_where_ it is deployed.

:::

#### Self Hosted MongoDB

Airbyte does not support self-signed SSL certificates for SSH tunnels.

#### AWS DocumentDB

The Airbyte connector does not support custom SSL certificates, which DocumentDB requires.
