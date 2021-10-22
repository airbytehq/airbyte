{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    children,
    _airbyte_emitted_at
from {{ ref('unnest_alias_ab1') }}
-- unnest_alias

