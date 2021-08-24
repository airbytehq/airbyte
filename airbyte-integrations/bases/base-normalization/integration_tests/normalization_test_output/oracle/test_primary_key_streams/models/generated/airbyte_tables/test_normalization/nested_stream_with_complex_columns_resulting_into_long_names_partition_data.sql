{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_PARTITION_HASHID') }},
    currency,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DATA_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3') }}
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

