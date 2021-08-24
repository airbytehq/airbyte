{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    currency,
    {{ QUOTE('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_EXCHANGE_RATE_HASHID') }}
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', 'airbyte_raw_exchange_rate') }}

