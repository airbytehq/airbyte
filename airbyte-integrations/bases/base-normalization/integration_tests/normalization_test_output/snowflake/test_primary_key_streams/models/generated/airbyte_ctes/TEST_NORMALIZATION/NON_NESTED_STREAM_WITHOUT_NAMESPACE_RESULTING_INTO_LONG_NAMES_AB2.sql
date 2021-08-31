{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_string() }}) as ID,
    cast(DATE as {{ dbt_utils.type_string() }}) as DATE,
    _AIRBYTE_EMITTED_AT
from {{ ref('NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB1') }}
-- NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES

