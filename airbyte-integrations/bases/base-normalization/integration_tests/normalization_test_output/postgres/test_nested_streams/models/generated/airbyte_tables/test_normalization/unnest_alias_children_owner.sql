{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'hash'}],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "test_normalization",
    tags = [ "nested" ]
) }}
-- Final base SQL model
select
    _airbyte_children_hashid,
    owner_id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_owner_hashid
from {{ ref('unnest_alias_children_owner_ab3') }}
-- owner at unnest_alias/children/owner from {{ ref('unnest_alias_children') }}
where 1 = 1

