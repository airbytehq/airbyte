{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('UNNEST_ALIAS', 'UNNEST_ALIAS', 'CHILDREN') }}
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    {{ json_extract_scalar(unnested_column_value('CHILDREN'), ['ab_id'], ['ab_id']) }} as AB_ID,
    {{ json_extract('', unnested_column_value('CHILDREN'), ['owner'], ['owner']) }} as OWNER,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('UNNEST_ALIAS') }} as table_alias
-- CHILDREN at unnest_alias/children
{{ cross_join_unnest('UNNEST_ALIAS', 'CHILDREN') }}
where 1 = 1
and CHILDREN is not null

