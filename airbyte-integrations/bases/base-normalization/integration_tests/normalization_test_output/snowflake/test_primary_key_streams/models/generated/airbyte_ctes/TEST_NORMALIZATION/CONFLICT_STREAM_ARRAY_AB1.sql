{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract('table_alias', '_airbyte_data', ['conflict_stream_array'], ['conflict_stream_array']) }} as CONFLICT_STREAM_ARRAY,
    _airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_CONFLICT_STREAM_ARRAY') }} as table_alias
-- CONFLICT_STREAM_ARRAY

