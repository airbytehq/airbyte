# test_primary_key_streams

This test suite is focusing on testing a stream of data similar to `source-exchangerates` using two different
`destination_sync_modes`:
- `incremental` + `overwrite`
- `incremental` + `append_dedup`

To do so, we've setup two streams in the catalog.json and are using the exact same record messages data in both.

Note that we are also making sure that one of the column used as primary key is of type `float` as this could be
an edge case using it as partition key on certain destinations.

