{{ config(alias="DEDUP_EXCHANGE_RATE_AB2", schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_bigint() }}) as ID,
    cast(CURRENCY as {{ dbt_utils.type_string() }}) as CURRENCY,
    cast(DATE as {{ dbt_utils.type_string() }}) as DATE,
    cast(HKD as {{ dbt_utils.type_float() }}) as HKD,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    _airbyte_emitted_at
from {{ ref('DEDUP_EXCHANGE_RATE_AB1_281') }}
-- DEDUP_EXCHANGE_RATE

