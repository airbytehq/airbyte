{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stre__nto_long_names_hashid,
    {{ json_extract_array(adapter.quote('partition'), ['double_array_data']) }} as double_array_data,
    {{ json_extract_array(adapter.quote('partition'), ['DATA']) }} as {{ adapter.quote('DATA') }},
    _airbyte_emitted_at
from {{ ref('nested_stream_with_c__lting_into_long_names') }}
where {{ adapter.quote('partition') }} is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

