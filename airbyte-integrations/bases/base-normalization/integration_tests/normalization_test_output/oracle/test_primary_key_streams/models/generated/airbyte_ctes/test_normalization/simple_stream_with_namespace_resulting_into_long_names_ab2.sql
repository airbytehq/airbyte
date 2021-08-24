{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_string() }}) as id,
    cast({{ QUOTE('DATE') }} as {{ dbt_utils.type_string() }}) as {{ QUOTE('DATE') }},
    airbyte_emitted_at
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab1') }}
-- simple_stream_with_namespace_resulting_into_long_names

