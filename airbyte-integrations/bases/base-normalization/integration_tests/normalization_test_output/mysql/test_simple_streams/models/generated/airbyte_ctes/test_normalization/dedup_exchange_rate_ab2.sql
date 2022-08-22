{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('dedup_exchange_rate_ab1') }}
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(currency as {{ dbt_utils.type_string() }}(1024)) as currency,
        case when {{ adapter.quote('date') }} = '' then NULL
        else cast({{ adapter.quote('date') }} as date)
        end as {{ adapter.quote('date') }}
        ,
    cast({{ empty_string_to_null('timestamp_col') }} as {{ type_timestamp_with_timezone() }}) as timestamp_col,
    cast({{ adapter.quote('HKD@spéçiäl & characters') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('HKD@spéçiäl & characters') }},
    cast(hkd_special___characters as {{ dbt_utils.type_string() }}(1024)) as hkd_special___characters,
    cast(nzd as {{ dbt_utils.type_float() }}) as nzd,
    cast(usd as {{ dbt_utils.type_float() }}) as usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('dedup_exchange_rate_ab1') }}
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

