{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "test_normalization",
    tags = [ "nested" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('conflict_stream_name___conflict_stream_name_ab3') }}
select
    _airbyte_conflict_stream_name_2_hashid,
    groups,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_conflict_stream_name_3_hashid
from {{ ref('conflict_stream_name___conflict_stream_name_ab3') }}
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name from {{ ref('conflict_stream_name_conflict_stream_name') }}
where 1 = 1

