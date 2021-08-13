{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CONFLICT_STREAM_ARRAY,
    _airbyte_emitted_at,
    _AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID
from {{ ref('CONFLICT_STREAM_ARRAY_AB3') }}
-- CONFLICT_STREAM_ARRAY from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_CONFLICT_STREAM_ARRAY') }}

