{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "TEST_NORMALIZATION",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    ID,
    CHILDREN,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_UNNEST_ALIAS_HASHID
from {{ ref('UNNEST_ALIAS_AB3') }}
-- UNNEST_ALIAS from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_UNNEST_ALIAS') }}
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT') }}

