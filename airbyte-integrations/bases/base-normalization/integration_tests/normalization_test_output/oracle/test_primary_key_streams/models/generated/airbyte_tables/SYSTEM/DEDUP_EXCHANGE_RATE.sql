{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    {{ QUOTE('DATE') }},
    TIMESTAMP_COL,
    HKD_SPECIAL___CHARACTERS,
    HKD_SPECIAL___CHARACTERS_1,
    NZD,
    USD,
    airbyte_emitted_at,
    AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('DEDUP_EXCHANGE_RATE_SCD') }}
-- DEDUP_EXCHANGE_RATE from {{ source('SYSTEM', 'AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where airbyte_active_row = 'Latest'

