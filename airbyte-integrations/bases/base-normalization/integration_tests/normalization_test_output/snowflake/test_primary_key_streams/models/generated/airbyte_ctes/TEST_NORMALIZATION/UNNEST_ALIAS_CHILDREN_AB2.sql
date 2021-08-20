{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    cast(AB_ID as {{ dbt_utils.type_bigint() }}) as AB_ID,
    cast(OWNER as {{ type_json() }}) as OWNER,
    _airbyte_emitted_at
from {{ ref('UNNEST_ALIAS_CHILDREN_AB1') }}
-- CHILDREN at unnest_alias/children

