{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as id,
    {{ json_extract_scalar('airbyte_data', ['date'], ['date']) }} as {{ QUOTE('DATE') }},
    {{ json_extract('table_alias', 'airbyte_data', ['partition'], ['partition']) }} as partition,
    airbyte_emitted_at
from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }} 
-- nested_stream_with_complex_columns_resulting_into_long_names

