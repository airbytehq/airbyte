{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_bigint() }}) as ID,
    CHILDREN,
    _AIRBYTE_EMITTED_AT
from {{ ref('UNNEST_ALIAS_AB1') }}
-- UNNEST_ALIAS

