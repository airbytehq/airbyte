{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('types_testing_ab1') }}
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_bigint() }}) as {{ adapter.quote('id') }},
    cast(airbyte_integer_column as {{ dbt_utils.type_bigint() }}) as airbyte_integer_column,
    cast(nullable_airbyte_integer_column as {{ dbt_utils.type_bigint() }}) as nullable_airbyte_integer_column,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('types_testing_ab1') }}
-- types_testing
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

