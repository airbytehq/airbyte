{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('UNNEST_ALIAS', 'UNNEST_ALIAS', 'CHILDREN') }}
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    {{ json_extract_scalar(unnested_column_value('CHILDREN'), ['ab_id'], ['ab_id']) }} as AB_ID,
    {{ json_extract('', unnested_column_value('CHILDREN'), ['owner'], ['owner']) }} as OWNER,
    _airbyte_emitted_at
from {{ ref('UNNEST_ALIAS') }} as table_alias
{{ cross_join_unnest('UNNEST_ALIAS', 'CHILDREN') }}
where CHILDREN is not null
-- CHILDREN at unnest_alias/children

