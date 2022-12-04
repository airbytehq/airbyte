{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('unnest_alias_children') }}
select
    _airbyte_children_hashid,
    {{ json_extract_scalar(adapter.quote('owner'), ['owner_id'], ['owner_id']) }} as owner_id,
    {{ json_extract_array(adapter.quote('owner'), ['column`_\'with"_quotes'], ['column___with__quotes']) }} as {{ adapter.quote('column`_\'with""_quotes') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('unnest_alias_children') }} as table_alias
-- owner at unnest_alias/children/owner
where 1 = 1
and {{ adapter.quote('owner') }} is not null

