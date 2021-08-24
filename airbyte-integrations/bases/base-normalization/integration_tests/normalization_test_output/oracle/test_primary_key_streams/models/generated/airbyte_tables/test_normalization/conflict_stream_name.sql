{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    conflict_stream_name,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }}
from {{ ref('conflict_stream_name_ab3') }}
-- conflict_stream_name from {{ source('test_normalization', 'airbyte_raw_conflict_stream_name') }}

