{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('unnest_alias_children_owner_ab1') }}
select
    _airbyte_children_hashid,
    cast(owner_id as {{ dbt_utils.type_bigint() }}) as owner_id,
    {{ adapter.quote('column`_\'with""_quotes') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('unnest_alias_children_owner_ab1') }}
-- owner at unnest_alias/children/owner
where 1 = 1

