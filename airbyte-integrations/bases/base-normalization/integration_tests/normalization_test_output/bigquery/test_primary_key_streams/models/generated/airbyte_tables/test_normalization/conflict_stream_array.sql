{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    conflict_stream_array,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_hashid
from {{ ref('conflict_stream_array_ab3') }}
-- conflict_stream_array from {{ source('test_normalization', '_airbyte_raw_conflict_stream_array') }}

