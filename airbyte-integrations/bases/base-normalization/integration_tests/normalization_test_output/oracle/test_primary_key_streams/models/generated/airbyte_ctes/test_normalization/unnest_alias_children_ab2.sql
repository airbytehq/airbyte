{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    {{ quote('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    cast(ab_id as {{ dbt_utils.type_bigint() }}) as ab_id,
    cast(owner as {{ type_json() }}) as owner,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('unnest_alias_children_ab1') }}
-- children at unnest_alias/children

