{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('conflict_stream_name') }}
select
    _airbyte_conflict_stream_name_hashid,
    {{ json_extract('table_alias', 'conflict_stream_name', ['conflict_stream_name'], ['conflict_stream_name']) }} as conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('conflict_stream_name') }} as table_alias
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
where 1 = 1
and conflict_stream_name is not null

