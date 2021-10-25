{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_data_hashid
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3') }}
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

