{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID,
    {{ json_extract_array('CONFLICT_STREAM_ARRAY', ['conflict_stream_name']) }} as CONFLICT_STREAM_NAME,
    airbyte_emitted_at
from {{ ref('CONFLICT_STREAM_ARRAY') }}
where CONFLICT_STREAM_ARRAY is not null
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array

