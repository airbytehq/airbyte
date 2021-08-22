{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CONFLICT_STREAM_NAME,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }}
from {{ ref('CONFLICT_STREAM_NAME_AB3') }}
-- CONFLICT_STREAM_NAME from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_CONFLICT_STREAM_NAME') }}

