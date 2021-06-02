{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    cast(date as {{ dbt_utils.type_string() }}) as date,
    cast(HKD_special___characters as {{ dbt_utils.type_float() }}) as HKD_special___characters,
    cast(HKD_special___characters_1 as {{ dbt_utils.type_string() }}) as HKD_special___characters_1,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    _airbyte_emitted_at
from {{ ref('exchange_rate_ab1') }}
-- exchange_rate

