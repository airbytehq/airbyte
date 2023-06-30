## Incremental syncs
The file-based connectors supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                                        | Supported? |
| :--------------------------------------------- |:-----------|
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files \(pattern matching\)  | Yes        |
| Replicate Multiple Streams \(distinct tables\) | Yes        |
| Namespaces                                     | No         |

We recommend you do not 

### Incremental sync 
After the initial sync, the connector only pulls files that were modified since the last sync.

The connector checkpoints the connection states when it is done syncing all files for a given timestamp. The connection's state only keeps track of the last 10 000 files synced. If more than 10 000 files are synced, the connector won't be able to rely on the connection state to deduplicate files. In this case, the connector will initialize its cursor to the minimum between the earliest file in the history, or 3 days ago.

Both the maximum number of files, and the time buffer can be configured by connector developers.