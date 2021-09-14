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
  {{ quote('DATE') }} as {{ quote('_AIRBYTE_START_AT') }},
  lag({{ quote('DATE') }}) over (
    partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
    order by {{ quote('DATE') }} asc nulls first, {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
  ) as {{ quote('_AIRBYTE_END_AT') }},
  case when lag({{ quote('DATE') }}) over (
    partition by id, currency, cast(nzd as {{ dbt_utils.type_string() }})
    order by {{ quote('DATE') }} asc nulls first, {{ quote('DATE') }} desc, {{ quote('_AIRBYTE_EMITTED_AT') }} desc
  ) is null  then 1 else 0 end as {{ quote('_AIRBYTE_ACTIVE_ROW') }},
  {{ quote('_AIRBYTE_EMITTED_AT') }},
  {{ quote('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }}
from {{ ref('dedup_exchange_rate_ab4') }}
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
where "_AIRBYTE_ROW_NUM" = 1

