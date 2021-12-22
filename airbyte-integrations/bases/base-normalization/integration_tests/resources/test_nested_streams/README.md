# test_nested_streams

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

# Stream name conflicts

`conflict_stream_name_*` tables and `unnest_alias` are testing naming conflicts between stream and columns names when combined with nesting
