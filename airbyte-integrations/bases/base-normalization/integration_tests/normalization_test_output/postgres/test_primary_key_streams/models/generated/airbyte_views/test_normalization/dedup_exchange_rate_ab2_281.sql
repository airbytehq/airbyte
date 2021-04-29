{{ config(alias="dedup_exchange_rate_ab2", schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_bigint() }}) as {{ adapter.quote('id') }},
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    cast({{ adapter.quote('date') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('date') }},
    cast(hkd as {{ dbt_utils.type_float() }}) as hkd,
    cast(nzd as {{ dbt_utils.type_float() }}) as nzd,
    cast(usd as {{ dbt_utils.type_float() }}) as usd,
    _airbyte_emitted_at
from {{ ref('dedup_exchange_rate_ab1_281') }}
-- dedup_exchange_rate

