{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_strea__nto_long_names_hashid,
    {{ json_extract_array(adapter.quote('partition'), ['double_array_data'], ['double_array_data']) }} as double_array_data,
    {{ json_extract_array(adapter.quote('partition'), ['DATA'], ['DATA']) }} as {{ adapter.quote('DATA') }},
    {{ json_extract_array(adapter.quote('partition'), ['column`_\'with"_quotes'], ['column___with__quotes']) }} as {{ adapter.quote('column__\'with"_quotes') }},
    _airbyte_emitted_at
from {{ ref('nested_stream_with_co__lting_into_long_names') }} as table_alias
where {{ adapter.quote('partition') }} is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

