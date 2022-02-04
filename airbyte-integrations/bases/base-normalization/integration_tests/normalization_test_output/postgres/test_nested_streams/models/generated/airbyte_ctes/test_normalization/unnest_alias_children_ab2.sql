{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('unnest_alias_children_ab1') }}
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as {{ dbt_utils.type_bigint() }}) as ab_id,
    cast({{ adapter.quote('owner') }} as {{ type_json() }}) as {{ adapter.quote('owner') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('unnest_alias_children_ab1') }}
-- children at unnest_alias/children
where 1 = 1

