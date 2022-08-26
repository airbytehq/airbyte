{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('multiple_column_names_conflicts_ab1') }}
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_bigint() }}) as {{ adapter.quote('id') }},
    cast({{ adapter.quote('User Id') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('User Id') }},
    cast(user_id as {{ dbt_utils.type_float() }}) as user_id,
    cast({{ adapter.quote('User id') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('User id') }},
    cast({{ adapter.quote('user id') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('user id') }},
    cast({{ adapter.quote('User@Id') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('User@Id') }},
    cast(userid as {{ dbt_utils.type_float() }}) as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('multiple_column_names_conflicts_ab1') }}
-- multiple_column_names_conflicts
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

