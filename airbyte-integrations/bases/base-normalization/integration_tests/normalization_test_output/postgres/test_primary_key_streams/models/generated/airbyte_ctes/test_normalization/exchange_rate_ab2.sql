{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_bigint() }}) as {{ adapter.quote('id') }},
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    cast({{ adapter.quote('date') }} as {{ type_date() }}) as {{ adapter.quote('date') }},
    cast(timestamp_col as {{ type_timestamp_with_timezone() }}) as timestamp_col,
    cast({{ adapter.quote('HKD@spéçiäl & characters') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('HKD@spéçiäl & characters') }},
    cast(hkd_special___characters as {{ dbt_utils.type_string() }}) as hkd_special___characters,
    cast(nzd as {{ dbt_utils.type_float() }}) as nzd,
    cast(usd as {{ dbt_utils.type_float() }}) as usd,
    _airbyte_emitted_at
from {{ ref('exchange_rate_ab1') }}
-- exchange_rate

