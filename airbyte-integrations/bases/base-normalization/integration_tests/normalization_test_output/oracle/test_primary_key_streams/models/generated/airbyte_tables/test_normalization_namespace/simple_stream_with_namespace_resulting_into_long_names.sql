{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    {{ quote('DATE') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab3') }}
-- simple_stream_with_namespace_resulting_into_long_names from {{ source('test_normalization_namespace', 'airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }}

