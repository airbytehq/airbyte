{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_PARTITION_HASHID') }},
    id,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DOUBLE_ARRAY_DATA_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3') }}
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

