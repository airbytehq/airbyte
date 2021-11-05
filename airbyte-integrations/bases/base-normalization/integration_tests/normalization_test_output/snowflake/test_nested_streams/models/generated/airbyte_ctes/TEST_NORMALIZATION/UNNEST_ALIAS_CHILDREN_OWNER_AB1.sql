{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CHILDREN_HASHID,
    {{ json_extract_scalar('OWNER', ['owner_id'], ['owner_id']) }} as OWNER_ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('UNNEST_ALIAS_CHILDREN') }} as table_alias
-- OWNER at unnest_alias/children/owner
where 1 = 1
and OWNER is not null

