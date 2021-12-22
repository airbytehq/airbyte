{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('unnest_alias_ab3') }}
select
    {{ adapter.quote('id') }},
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_unnest_alias_hashid
from {{ ref('unnest_alias_ab3') }}
-- unnest_alias from {{ source('test_normalization', '_airbyte_raw_unnest_alias') }}
where 1 = 1

