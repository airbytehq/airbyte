{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    cast({{ quote('DATE') }} as {{ type_date() }}) as {{ quote('DATE') }},
    cast(timestamp_col as {{ type_timestamp_with_timezone() }}) as timestamp_col,
    cast(hkd_special___characters as {{ dbt_utils.type_float() }}) as hkd_special___characters,
    cast(hkd_special___characters_1 as {{ dbt_utils.type_string() }}) as hkd_special___characters_1,
    cast(nzd as {{ dbt_utils.type_float() }}) as nzd,
    cast(usd as {{ dbt_utils.type_float() }}) as usd,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('exchange_rate_ab1') }}
-- exchange_rate

