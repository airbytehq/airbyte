{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('conflict_stream_array_conflict_stream_array', 'conflict_stream_array', 'conflict_stream_name') }}
select
    _airbyte_conflict_stream_array_2_hashid,
    {{ json_extract_scalar(unnested_column_value('conflict_stream_name'), ['id'], ['id']) }} as {{ adapter.quote('id') }},
    _airbyte_emitted_at
from {{ ref('conflict_stream_array_conflict_stream_array') }} as table_alias
{{ cross_join_unnest('conflict_stream_array', 'conflict_stream_name') }}
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name

