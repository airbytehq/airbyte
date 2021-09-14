{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID') }},
    groups,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_CONFLICT_STREAM_NAME_3_HASHID') }}
from {{ ref('conflict_stream_name_conflict_stream_name_conflict_stream_name_ab3') }}
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name from {{ ref('conflict_stream_name_conflict_stream_name') }}

