{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CONFLICT_STREAM_ARRAY,
    airbyte_emitted_at,
    AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID
from {{ ref('CONFLICT_STREAM_ARRAY_AB3') }}
-- CONFLICT_STREAM_ARRAY from {{ source('SYSTEM', 'AIRBYTE_RAW_CONFLICT_STREAM_ARRAY') }}

