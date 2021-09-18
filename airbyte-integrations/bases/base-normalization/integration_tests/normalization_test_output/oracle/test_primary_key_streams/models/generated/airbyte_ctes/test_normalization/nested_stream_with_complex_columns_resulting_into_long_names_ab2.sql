{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_string() }}) as id,
    cast({{ quote('DATE') }} as {{ dbt_utils.type_string() }}) as {{ quote('DATE') }},
    cast(partition as {{ type_json() }}) as partition,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab1') }}
-- nested_stream_with_complex_columns_resulting_into_long_names

