# test_simple_streams

## Exchange Rate

This test suite is focusing on testing a simple stream (non-nested) of data similar to `source-exchangerates` using two different
`destination_sync_modes`:

- `incremental` + `overwrite` with stream `exchange_rate`
- `incremental` + `append_dedup` with stream `dedup_exchange_rate`

To do so, we've setup two streams in the catalog.json and are using the exact same record messages data in both.

Note that we are also making sure that one of the column used as primary key is of type `float` as this could be
an edge case using it as partition key on certain destinations.

# CDC

We've also included some streams as if they were produced by a CDC source, especially to test how they would behave regarding dedup sync modes where deleted rows should be removed from deduplicated tables
