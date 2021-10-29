{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "TEST_NORMALIZATION",
    tags = [ "nested" ]
) }}
-- Final base SQL model
select
    _AIRBYTE_CHILDREN_HASHID,
    OWNER_ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_OWNER_HASHID
from {{ ref('UNNEST_ALIAS_CHILDREN_OWNER_AB3') }}
-- OWNER at unnest_alias/children/owner from {{ ref('UNNEST_ALIAS_CHILDREN') }}
where 1 = 1

