{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }},
    {{ json_extract('table_alias', 'conflict_stream_name', ['conflict_stream_name'], ['conflict_stream_name']) }} as conflict_stream_name,
    airbyte_emitted_at
from {{ ref('conflict_stream_name') }} 
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name

