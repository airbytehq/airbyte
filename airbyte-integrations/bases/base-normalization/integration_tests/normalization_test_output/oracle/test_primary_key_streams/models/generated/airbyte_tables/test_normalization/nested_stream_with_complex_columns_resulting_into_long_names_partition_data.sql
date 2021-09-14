{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_PARTITION_HASHID') }},
    currency,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_DATA_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3') }}
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

