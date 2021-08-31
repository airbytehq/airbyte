{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    {{ adapter.quote('DATA') }},
    {{ adapter.quote('column__\'with"_quotes') }},
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from {{ ref('nested_stream_with_co_2g_names_partition_ab3') }}
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from {{ ref('nested_stream_with_co__lting_into_long_names') }}

