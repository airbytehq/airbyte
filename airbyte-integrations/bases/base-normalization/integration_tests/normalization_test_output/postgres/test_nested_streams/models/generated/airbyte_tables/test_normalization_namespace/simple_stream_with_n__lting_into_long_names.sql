{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'hash'}],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "test_normalization_namespace",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    {{ adapter.quote('id') }},
    {{ adapter.quote('date') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_simple_stre__nto_long_names_hashid
from {{ ref('simple_stream_with_n__lting_into_long_names_ab3') }}
-- simple_stream_with_n__lting_into_long_names from {{ source('test_normalization_namespace', '_airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }}
where 1 = 1

