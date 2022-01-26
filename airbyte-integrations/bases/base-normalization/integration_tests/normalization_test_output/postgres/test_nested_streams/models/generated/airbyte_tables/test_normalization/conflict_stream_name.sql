{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('conflict_stream_name_ab3') }}
select
    {{ adapter.quote('id') }},
    conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_conflict_stream_name_hashid
from {{ ref('conflict_stream_name_ab3') }}
-- conflict_stream_name from {{ source('test_normalization', '_airbyte_raw_conflict_stream_name') }}
where 1 = 1

