{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('dedup_exchange_rate_ab1') }}
select
    TRY_CAST(id as {{ dbt_utils.type_bigint() }}) as id,
    TRY_CAST(TRIM('"' FROM currency) AS {{ dbt_utils.type_string() }}) as currency,
    TRY_CAST(TRIM('"' FROM {{ empty_string_to_null(adapter.quote('date')) }}) AS DATE) as {{ adapter.quote('date') }},
    TRY_CAST(TRIM('"' FROM {{ empty_string_to_null('timestamp_col') }}) AS DATETIME) as timestamp_col,
    TRY_CAST(HKD_special___characters as {{ dbt_utils.type_float() }}) as HKD_special___characters,
    TRY_CAST(TRIM('"' FROM HKD_special___characters_1) AS {{ dbt_utils.type_string() }}) as HKD_special___characters_1,
    TRY_CAST(NZD as {{ dbt_utils.type_float() }}) as NZD,
    TRY_CAST(USD as {{ dbt_utils.type_float() }}) as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('dedup_exchange_rate_ab1') }}
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

