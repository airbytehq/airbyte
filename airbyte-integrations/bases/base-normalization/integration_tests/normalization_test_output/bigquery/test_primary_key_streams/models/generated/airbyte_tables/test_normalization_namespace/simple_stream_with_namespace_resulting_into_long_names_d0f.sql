{{ config(alias="simple_stream_with_namespace_resulting_into_long_names", schema="test_normalization_namespace", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab3_4fe') }}
-- simple_stream_with_namespace_resulting_into_long_names from {{ source('test_normalization_namespace', '_airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }}

