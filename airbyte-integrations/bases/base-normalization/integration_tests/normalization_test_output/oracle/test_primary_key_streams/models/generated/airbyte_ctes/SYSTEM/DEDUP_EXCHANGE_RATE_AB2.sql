{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_bigint() }}) as ID,
    cast(CURRENCY as {{ dbt_utils.type_string() }}) as CURRENCY,
    cast({{ QUOTE('DATE') }} as {{ dbt_utils.type_string() }}) as {{ QUOTE('DATE') }},
    cast(TIMESTAMP_COL as {{ dbt_utils.type_string() }}) as TIMESTAMP_COL,
    cast(HKD_SPECIAL___CHARACTERS as {{ dbt_utils.type_float() }}) as HKD_SPECIAL___CHARACTERS,
    cast(HKD_SPECIAL___CHARACTERS_1 as {{ dbt_utils.type_string() }}) as HKD_SPECIAL___CHARACTERS_1,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    airbyte_emitted_at
from {{ ref('DEDUP_EXCHANGE_RATE_AB1') }}
-- DEDUP_EXCHANGE_RATE

