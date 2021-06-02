{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('id') }},
    cast({{ adapter.quote('date') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('date') }},
    cast({{ adapter.quote('partition') }} as {{ type_json() }}) as {{ adapter.quote('partition') }},
    _airbyte_emitted_at
from {{ ref('nested_stream_with_c__lting_into_long_names_ab1') }}
-- nested_stream_with_c__lting_into_long_names

