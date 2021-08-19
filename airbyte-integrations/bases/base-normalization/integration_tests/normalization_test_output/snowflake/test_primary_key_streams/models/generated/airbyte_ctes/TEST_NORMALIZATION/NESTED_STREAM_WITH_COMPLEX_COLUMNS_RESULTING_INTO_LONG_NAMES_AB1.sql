{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as DATE,
    {{ json_extract('table_alias', '_airbyte_data', ['partition'], ['partition']) }} as PARTITION,
    _airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }} as table_alias
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES

