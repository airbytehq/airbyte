{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    {{ adapter.quote('date') }},
    timestamp_col,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    hkd_special___characters,
    nzd,
    usd,
    {{ adapter.quote('date') }} as _airbyte_start_at,
    lag({{ adapter.quote('date') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ adapter.quote('date') }} is null asc, {{ adapter.quote('date') }} desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag({{ adapter.quote('date') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ adapter.quote('date') }} is null asc, {{ adapter.quote('date') }} desc, _airbyte_emitted_at desc
    ) is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from {{ ref('dedup_exchange_rate_ab4') }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
where _airbyte_row_num = 1

