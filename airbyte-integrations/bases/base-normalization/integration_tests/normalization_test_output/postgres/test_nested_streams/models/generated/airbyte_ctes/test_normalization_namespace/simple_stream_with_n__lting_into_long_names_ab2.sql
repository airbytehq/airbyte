{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization_namespace",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('simple_stream_with_n__lting_into_long_names_ab1') }}
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('id') }},
    cast({{ adapter.quote('date') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('date') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('simple_stream_with_n__lting_into_long_names_ab1') }}
-- simple_stream_with_n__lting_into_long_names
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

