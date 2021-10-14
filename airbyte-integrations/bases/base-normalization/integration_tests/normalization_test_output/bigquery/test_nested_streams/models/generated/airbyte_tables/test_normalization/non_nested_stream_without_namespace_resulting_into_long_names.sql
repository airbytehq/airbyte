{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid
from {{ ref('non_nested_stream_without_namespace_resulting_into_long_names_ab3') }}
-- non_nested_stream_without_namespace_resulting_into_long_names from {{ source('test_normalization', '_airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names') }}

