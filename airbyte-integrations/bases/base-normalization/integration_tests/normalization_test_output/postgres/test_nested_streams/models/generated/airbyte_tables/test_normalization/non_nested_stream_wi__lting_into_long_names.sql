{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('non_nested_stream_wi__lting_into_long_names_ab3') }}
select
    {{ adapter.quote('id') }},
    {{ adapter.quote('date') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_non_nested___nto_long_names_hashid
from {{ ref('non_nested_stream_wi__lting_into_long_names_ab3') }}
-- non_nested_stream_wi__lting_into_long_names from {{ source('test_normalization', '_airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names') }}
where 1 = 1

