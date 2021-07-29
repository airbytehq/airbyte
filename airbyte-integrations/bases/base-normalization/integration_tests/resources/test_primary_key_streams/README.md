# test_primary_key_streams

This test suite is focusing on testing a stream of data similar to `source-exchangerates` using two different
`destination_sync_modes`:
- `incremental` + `overwrite` with stream `exchange_rate`
- `incremental` + `append_dedup` with stream `dedup_exchange_rate`

To do so, we've setup two streams in the catalog.json and are using the exact same record messages data in both.

Note that we are also making sure that one of the column used as primary key is of type `float` as this could be
an edge case using it as partition key on certain destinations.

# Nested streams

The stream `nested_stream_with_complex_columns_resulting_into_long_names` is testing primary key definition on a stream
with nested fields with different complex types:

- nested object
- nested array
- nested array of array

# Stream names collisions

The following three streams are purposely named with very long descriptions to break postgres 64 characters limits:
(even if they are set in different schemas)

- `test_normalization_nested_stream_with_complex_columns_resulting_into_long_names`
- `test_normalization_non_nested_stream_without_namespace_resulting_into_long_names`
- `test_normalization_namespace_simple_stream_with_namespace_resulting_into_long_names`

which could all be truncated into:

- `test_normalization_n__lting_into_long_names`

Resulting into collisions...
