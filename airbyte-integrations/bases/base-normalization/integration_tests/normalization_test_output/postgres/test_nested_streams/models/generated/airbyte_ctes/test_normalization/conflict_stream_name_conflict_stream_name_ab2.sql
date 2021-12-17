{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('conflict_stream_name_conflict_stream_name_ab1') }}
select
    _airbyte_conflict_stream_name_hashid,
    cast(conflict_stream_name as {{ type_json() }}) as conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('conflict_stream_name_conflict_stream_name_ab1') }}
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
where 1 = 1

