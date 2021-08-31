{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    {{ quote('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    {{ quote('DATE') }} as "_AIRBYTE_START_AT",
    lag({{ quote('DATE') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
    ) as "_AIRBYTE_END_AT", 
    coalesce(cast(lag({{ quote('DATE') }}) over (
        partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
        order by {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
    ) as varchar(200)), 'Latest') as "_AIRBYTE_ACTIVE_ROW",
    "_AIRBYTE_EMITTED_AT",
    {{ quote('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }}
from {{ ref('dedup_exchange_rate_ab4') }}
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
where "_AIRBYTE_ROW_NUM" = 1

