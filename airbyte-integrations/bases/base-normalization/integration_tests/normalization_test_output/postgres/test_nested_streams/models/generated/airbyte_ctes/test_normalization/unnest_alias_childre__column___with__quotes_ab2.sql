{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('unnest_alias_childre__column___with__quotes_ab1') }}
select
    _airbyte_owner_hashid,
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('unnest_alias_childre__column___with__quotes_ab1') }}
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
where 1 = 1

