{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('nested_stream_with_co_1g_into_long_names_ab1') }}
select
    cast(id as {{ dbt_utils.type_string() }}(1024)) as id,
    cast({{ adapter.quote('date') }} as {{ dbt_utils.type_string() }}(1024)) as {{ adapter.quote('date') }},
    cast({{ adapter.quote('partition') }} as {{ type_json() }}) as {{ adapter.quote('partition') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('nested_stream_with_co_1g_into_long_names_ab1') }}
-- nested_stream_with_co__lting_into_long_names
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

