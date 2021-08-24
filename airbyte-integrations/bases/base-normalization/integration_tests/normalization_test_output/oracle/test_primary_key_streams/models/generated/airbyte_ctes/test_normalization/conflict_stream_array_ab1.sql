{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as id,
    {{ json_extract_array('airbyte_data', ['conflict_stream_array'], ['conflict_stream_array']) }} as conflict_stream_array,
    airbyte_emitted_at
from {{ source('test_normalization', 'airbyte_raw_conflict_stream_array') }} 
-- conflict_stream_array

