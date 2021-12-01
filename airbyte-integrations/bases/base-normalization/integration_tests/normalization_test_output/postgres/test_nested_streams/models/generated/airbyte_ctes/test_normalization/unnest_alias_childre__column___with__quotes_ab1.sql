{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('unnest_alias_children_owner') }}
{{ unnest_cte(ref('unnest_alias_children_owner'), 'owner', adapter.quote('column`_\'with""_quotes')) }}
select
    _airbyte_owner_hashid,
    {{ json_extract_scalar(unnested_column_value(adapter.quote('column`_\'with""_quotes')), ['currency'], ['currency']) }} as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('unnest_alias_children_owner') }} as table_alias
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
{{ cross_join_unnest('owner', adapter.quote('column`_\'with""_quotes')) }}
where 1 = 1
and {{ adapter.quote('column`_\'with""_quotes') }} is not null

