# Troubleshooting MongoDB Sources

## Connector Limitations

### MongoDB Oplog and Change Streams

[MongoDB's Change Streams](https://www.mongodb.com/docs/manual/changeStreams/) are based on the [Replica Set Oplog](https://www.mongodb.com/docs/manual/core/replica-set-oplog/). This has retention limitations. Syncs that run less frequently than the retention period of the Oplog may encounter issues with missing data.

We recommend adjusting the Oplog size for your MongoDB cluster to ensure it holds at least 24 hours of changes. For optimal results, we suggest expanding it to maintain a week's worth of data. To adjust your Oplog size, see the corresponding tutorials for [MongoDB Atlas](https://www.mongodb.com/docs/atlas/cluster-additional-settings/#set-oplog-size) (fully-managed) and [MongoDB shell](https://www.mongodb.com/docs/manual/tutorial/change-oplog-size/) (self-hosted).

If a sync fails with "Saved offset is not valid", the change stream position saved by the previous sync is no longer in the oplog. The **Invalid CDC position behavior** setting decides what happens: with "Fail sync" (the default) you need to reset the connection, with "Re-sync data" the connector takes a new initial snapshot by itself. To prevent it from happening again:

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

### MongoDB CDC Limitations

MongoDB has a 16MB maximum document size limit for BSON documents. During CDC (Change Data Capture) syncs, change stream events can exceed this limit when documents are large, causing a `BSONObjectTooLarge` error. This typically occurs during incremental syncs when change stream events include the full document content.

If you encounter this error, you have several options to resolve it:

1. Switch the affected stream to Full Refresh sync mode instead of Incremental mode. Full Refresh does not use change streams and is not subject to this limitation.
2. Restructure large documents in your MongoDB collection to stay under the 16MB limit.
3. Deselect streams containing documents that exceed the size limit.

For more information about MongoDB's document size limits, see the [MongoDB documentation on limits](https://www.mongodb.com/docs/manual/reference/limits/).

## How update events are captured

For an update event, Airbyte reads the document's current state when the event is processed (MongoDB's `updateLookup`).
If a document is updated several times in quick succession, or several times between two syncs, the records for those
events can all show the same final version of the document: **intermediate document states are not captured.** A
document that was deleted before the event could be read is emitted as a delete.

