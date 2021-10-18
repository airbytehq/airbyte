{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_partition_hashid,
    {{ adapter.quote('id') }},
    _airbyte_emitted_at,
    _airbyte_double_array_data_hashid
from {{ ref('nested_stream_with_c__ion_double_array_data_ab3') }}
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from {{ ref('nested_stream_with_c___long_names_partition') }}

