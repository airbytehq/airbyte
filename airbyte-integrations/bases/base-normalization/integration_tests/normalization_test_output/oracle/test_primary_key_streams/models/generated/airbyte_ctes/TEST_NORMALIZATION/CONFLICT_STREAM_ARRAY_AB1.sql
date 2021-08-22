{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_array('airbyte_data', ['conflict_stream_array'], ['conflict_stream_array']) }} as CONFLICT_STREAM_ARRAY,
    airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_CONFLICT_STREAM_ARRAY') }} 
-- CONFLICT_STREAM_ARRAY

