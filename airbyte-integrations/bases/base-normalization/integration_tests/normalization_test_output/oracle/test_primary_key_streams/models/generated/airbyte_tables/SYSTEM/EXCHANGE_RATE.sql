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
    AIRBYTE_EXCHANGE_RATE_HASHID
from {{ ref('EXCHANGE_RATE_AB3') }}
-- EXCHANGE_RATE from {{ source('SYSTEM', 'AIRBYTE_RAW_EXCHANGE_RATE') }}

