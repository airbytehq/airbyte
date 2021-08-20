{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CONFLICT_STREAM_NAME,
    airbyte_emitted_at,
    AIRBYTE_CONFLICT_STREAM_NAME_HASHID
from {{ ref('CONFLICT_STREAM_NAME_AB3') }}
-- CONFLICT_STREAM_NAME from {{ source('SYSTEM', 'AIRBYTE_RAW_CONFLICT_STREAM_NAME') }}

