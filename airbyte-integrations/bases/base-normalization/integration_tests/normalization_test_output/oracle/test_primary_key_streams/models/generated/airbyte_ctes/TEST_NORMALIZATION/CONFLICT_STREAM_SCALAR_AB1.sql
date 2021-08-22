{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('airbyte_data', ['conflict_stream_scalar'], ['conflict_stream_scalar']) }} as CONFLICT_STREAM_SCALAR,
    airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_CONFLICT_STREAM_SCALAR') }} 
-- CONFLICT_STREAM_SCALAR

