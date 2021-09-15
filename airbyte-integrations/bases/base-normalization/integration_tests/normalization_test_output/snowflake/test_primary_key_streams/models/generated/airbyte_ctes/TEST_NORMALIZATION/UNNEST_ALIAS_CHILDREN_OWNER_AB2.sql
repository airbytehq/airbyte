{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_CHILDREN_HASHID,
    cast(OWNER_ID as {{ dbt_utils.type_bigint() }}) as OWNER_ID,
    _AIRBYTE_EMITTED_AT
from {{ ref('UNNEST_ALIAS_CHILDREN_OWNER_AB1') }}
-- OWNER at unnest_alias/children/owner

