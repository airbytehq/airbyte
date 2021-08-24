{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    conflict_stream_scalar,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_SCALAR_HASHID') }}
from {{ ref('conflict_stream_scalar_ab3') }}
-- conflict_stream_scalar from {{ source('test_normalization', 'airbyte_raw_conflict_stream_scalar') }}

