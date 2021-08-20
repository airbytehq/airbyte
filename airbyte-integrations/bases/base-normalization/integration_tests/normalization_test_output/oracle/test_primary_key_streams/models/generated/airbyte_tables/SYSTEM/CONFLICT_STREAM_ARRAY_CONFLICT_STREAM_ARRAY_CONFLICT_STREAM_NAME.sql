{{ config(schema="SYSTEM", tags=["nested"]) }}
-- Final base SQL model
select
    AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    ID,
    airbyte_emitted_at,
    AIRBYTE_CONFLICT_STREAM_NAME_HASHID
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB3') }}
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY') }}

