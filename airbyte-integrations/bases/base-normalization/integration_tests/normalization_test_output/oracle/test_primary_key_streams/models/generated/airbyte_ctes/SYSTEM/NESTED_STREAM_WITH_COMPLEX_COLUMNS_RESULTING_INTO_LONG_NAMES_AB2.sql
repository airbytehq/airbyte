{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_string() }}) as ID,
    cast({{ QUOTE('DATE') }} as {{ dbt_utils.type_string() }}) as {{ QUOTE('DATE') }},
    cast(PARTITION as {{ type_json() }}) as PARTITION,
    airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB1') }}
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES

