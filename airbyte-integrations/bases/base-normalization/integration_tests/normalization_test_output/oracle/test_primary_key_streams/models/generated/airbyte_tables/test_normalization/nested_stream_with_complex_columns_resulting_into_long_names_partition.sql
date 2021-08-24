{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }},
    double_array_data,
    data,
    column___with__quotes,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_PARTITION_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3') }}
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names') }}

