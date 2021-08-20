{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id']) }} as ID,
    {{ json_extract_scalar('airbyte_data', ['date']) }} as {{ QUOTE('DATE') }},
    {{ json_extract('airbyte_data', ['partition']) }} as PARTITION,
    airbyte_emitted_at
from {{ source('SYSTEM', 'AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES

