{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_string() }}) as id,
    cast(date as {{ dbt_utils.type_string() }}) as date,
    _airbyte_emitted_at
from {{ ref('non_nested_stream_without_namespace_resulting_into_long_names_ab1') }}
-- non_nested_stream_without_namespace_resulting_into_long_names

