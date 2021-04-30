{{ config(alias="nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_ab1", schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    {{ json_extract_array(adapter.quote('partition'), ['double_array_data']) }} as double_array_data,
    {{ json_extract_array(adapter.quote('partition'), ['DATA']) }} as data,
    _airbyte_emitted_at
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_d67') }}
where {{ adapter.quote('partition') }} is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

