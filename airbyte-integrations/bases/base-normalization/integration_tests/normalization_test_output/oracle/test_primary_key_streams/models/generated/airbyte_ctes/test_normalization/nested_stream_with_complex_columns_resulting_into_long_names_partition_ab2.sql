{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }},
    double_array_data,
    data,
    column___with__quotes,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1') }}
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

