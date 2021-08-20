{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id']) }} as ID,
    {{ json_extract('airbyte_data', ['conflict_stream_name']) }} as CONFLICT_STREAM_NAME,
    airbyte_emitted_at
from {{ source('SYSTEM', 'AIRBYTE_RAW_CONFLICT_STREAM_NAME') }}
-- CONFLICT_STREAM_NAME

