{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    {{ quote('DATE') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('non_nested_stream_without_namespace_resulting_into_long_names_ab3') }}
-- non_nested_stream_without_namespace_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names') }}

