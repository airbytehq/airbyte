{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CONFLICT_STREAM_NAME_HASHID,
    {{ json_extract('table_alias', 'CONFLICT_STREAM_NAME', ['conflict_stream_name'], ['conflict_stream_name']) }} as CONFLICT_STREAM_NAME,
    _AIRBYTE_EMITTED_AT
from {{ ref('CONFLICT_STREAM_NAME') }} as table_alias
where CONFLICT_STREAM_NAME is not null
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name

