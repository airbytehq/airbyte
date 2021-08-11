{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_conflict_stream_array_2_hashid,
    id,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_name_hashid
from {{ ref('conflict_stream_array_conflict_stream_array_conflict_stream_name_ab3') }}
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name from {{ ref('conflict_stream_array_conflict_stream_array') }}

