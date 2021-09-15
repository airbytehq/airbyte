{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnest_cte('unnest_alias', 'unnest_alias', 'children') }}
select
    {{ quote('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    {{ json_extract_scalar(unnested_column_value('children'), ['ab_id'], ['ab_id']) }} as ab_id,
    {{ json_extract('', unnested_column_value('children'), ['owner'], ['owner']) }} as owner,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('unnest_alias') }} 
{{ cross_join_unnest('unnest_alias', 'children') }}
where children is not null
-- children at unnest_alias/children

