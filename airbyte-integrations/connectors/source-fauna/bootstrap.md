# Fauna Source

[Fauna](https://fauna.com/) is a serverless "document-relational" database that user's interact with via APIs. This connector delivers Fauna as an airbyte source.

This source is implemented in the [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).
It also uses the [Fauna Python Driver](https://docs.fauna.com/fauna/current/drivers/python), which
allows the connector to build FQL queries in python. This driver is what queries the Fauna database.

Fauna has collections (similar to tables) and documents (similar to rows).

Every document has at least 3 fields: `ref`, `ts` and `data`. The `ref` is a unique string identifier
for every document. The `ts` is a timestamp, which is the time that the document was last modified.
The `data` is arbitrary json data. Because there is no shape to this data, we also allow users of
airbyte to specify which fields of the document they want to export as top-level columns.

Users can also choose to export the `data` field itself in the raw and in the case of incremental syncs, metadata regarding when a document was deleted.

We currently only provide a single stream, which is the collection the user has chosen. This is
because to support incremental syncs we need an index with every collection, so it ends up being easier to just have the user
setup the index and tell us the collection and index name they wish to use.

## Full sync

This source will simply call the following [FQL](https://docs.fauna.com/fauna/current/api/fql/): `Paginate(Documents(Collection("collection-name")))`.
This queries all documents in the database in a paginated manner. The source then iterates over all the results from that query to export data from the connector.

Docs:
[Paginate](https://docs.fauna.com/fauna/current/api/fql/functions/paginate?lang=python).
[Documents](https://docs.fauna.com/fauna/current/api/fql/functions/documents?lang=python).
[Collection](https://docs.fauna.com/fauna/current/api/fql/functions/collection?lang=python).

## Incremental sync

### Updates (uses an index over ts)

The source will call FQL similar to this: `Paginate(Range(Match(Index("index-name")), <last-sync-ts>, []))`.
The index we match against has the values `ts` and `ref`, so it will sort by the time since the document
has been modified. The Range() will limit the query to just pull the documents that have been modified
since the last query.

Docs:
[Range](https://docs.fauna.com/fauna/current/api/fql/functions/range?lang=python).
[Match](https://docs.fauna.com/fauna/current/api/fql/functions/match?lang=python).
[Index](https://docs.fauna.com/fauna/current/api/fql/functions/iindex?lang=python).

### Deletes (uses the events API)

If the users wants deletes, we have a seperate query for that:
`Paginate(Events(Documents(Collection("collection-name"))))`. This will paginate over all the events
in the documents of the collection. We also filter this to only give us the events since the recently
modified documents. Using these events, we can produce a record with the "deleted at" field set, so
that users know the document has been deleted.

Docs:
[Events](https://docs.fauna.com/fauna/current/api/fql/functions/events?lang=python).
