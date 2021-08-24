{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    {{ QUOTE('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    {{ QUOTE('DATE') }} as airbyte_start_at,
    lag({{ QUOTE('DATE') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag({{ QUOTE('DATE') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }}
from {{ ref('dedup_exchange_rate_ab4') }}
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
where airbyte_row_num = 1

