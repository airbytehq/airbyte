{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_bigint() }}) as ID,
    cast(CURRENCY as {{ dbt_utils.type_string() }}) as CURRENCY,
    cast(DATE as {{ type_date() }}) as DATE,
    cast(TIMESTAMP_COL as {{ type_timestamp_with_timezone() }}) as TIMESTAMP_COL,
    cast({{ adapter.quote('HKD@spéçiäl & characters') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('HKD@spéçiäl & characters') }},
    cast(HKD_SPECIAL___CHARACTERS as {{ dbt_utils.type_string() }}) as HKD_SPECIAL___CHARACTERS,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    _AIRBYTE_EMITTED_AT
from {{ ref('DEDUP_EXCHANGE_RATE_AB1') }}
-- DEDUP_EXCHANGE_RATE

