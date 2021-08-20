{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY', 'CONFLICT_STREAM_ARRAY', 'CONFLICT_STREAM_NAME') }}
select
    AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    {{ json_extract_scalar(unnested_column_value('CONFLICT_STREAM_NAME'), ['id']) }} as ID,
    airbyte_emitted_at
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY') }}
{{ cross_join_unnest('CONFLICT_STREAM_ARRAY', 'CONFLICT_STREAM_NAME') }}
where CONFLICT_STREAM_NAME is not null
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name

