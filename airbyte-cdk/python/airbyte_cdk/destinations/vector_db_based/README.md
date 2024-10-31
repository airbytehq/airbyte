# Vector DB based destinations

## Note: All helpers in this directory are experimental and subject to change

This directory contains several helpers that can be used to create a destination that processes and chunks records, embeds their text part and loads them into a vector database.
The specific loading behavior is defined by the destination connector itself, but chunking and embedding behavior is handled by the helpers.

To use these helpers, install the CDK with the `vector-db-based` extra:

```bash
pip install airbyte-cdk[vector-db-based]
```

The helpers can be used in the following way:

- Add the config models to the spec of the connector
- Implement the `Indexer` interface for your specific database
- In the check implementation of the destination, initialize the indexer and the embedder and call `check` on them
- In the write implementation of the destination, initialize the indexer, the embedder and pass them to a new instance of the writer. Then call the writers `write` method with the iterable for incoming messages

If there are no connector-specific embedders, the `airbyte_cdk.destinations.vector_db_based.embedder.create_from_config` function can be used to get an embedder instance from the config.

This is how the components interact:

```text
┌─────────────┐
│MyDestination│
└┬────────────┘
┌▽───────────────────────────────┐
│Writer                          │
└┬─────────┬──────────┬──────────┘
┌▽───────┐┌▽────────┐┌▽────────────────┐
│Embedder││MyIndexer││DocumentProcessor│
└────────┘└─────────┘└─────────────────┘
```

Normally, only the `MyDestination` class and the `MyIndexer` class has to be implemented specifically for the destination. The other classes are provided as is by the helpers.
