{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract('table_alias', 'airbyte_data', ['conflict_stream_name'], ['conflict_stream_name']) }} as CONFLICT_STREAM_NAME,
    airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_CONFLICT_STREAM_NAME') }} 
-- CONFLICT_STREAM_NAME

