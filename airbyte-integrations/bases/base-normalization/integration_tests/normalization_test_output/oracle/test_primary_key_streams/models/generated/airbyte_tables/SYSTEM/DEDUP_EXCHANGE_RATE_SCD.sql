{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    CURRENCY,
    {{ QUOTE('DATE') }},
    TIMESTAMP_COL,
    HKD_SPECIAL___CHARACTERS,
    HKD_SPECIAL___CHARACTERS_1,
    NZD,
    USD,
    {{ QUOTE('DATE') }} as airbyte_start_at,
    lag({{ QUOTE('DATE') }}) over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag({{ QUOTE('DATE') }}) over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by {{ QUOTE('DATE') }} desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('DEDUP_EXCHANGE_RATE_AB4') }}
-- DEDUP_EXCHANGE_RATE from {{ source('SYSTEM', 'AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where airbyte_row_num = 1

