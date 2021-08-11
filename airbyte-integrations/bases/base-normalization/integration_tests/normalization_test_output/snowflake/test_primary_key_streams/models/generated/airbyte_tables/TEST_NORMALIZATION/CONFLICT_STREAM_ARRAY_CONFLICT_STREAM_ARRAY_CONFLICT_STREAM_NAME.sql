{{ config(schema="TEST_NORMALIZATION", tags=["nested"]) }}
-- Final base SQL model
select
    _AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    ID,
    _airbyte_emitted_at,
    _AIRBYTE_CONFLICT_STREAM_NAME_HASHID
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB3') }}
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY') }}

