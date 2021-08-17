{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID,
    {{ json_extract_array('CONFLICT_STREAM_ARRAY', ['conflict_stream_name'], ['conflict_stream_name']) }} as CONFLICT_STREAM_NAME,
    _airbyte_emitted_at
from {{ ref('CONFLICT_STREAM_ARRAY') }} as table_alias
where CONFLICT_STREAM_ARRAY is not null
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array

