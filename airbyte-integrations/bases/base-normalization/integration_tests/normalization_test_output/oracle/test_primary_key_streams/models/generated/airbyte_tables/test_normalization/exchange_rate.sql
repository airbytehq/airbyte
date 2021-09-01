{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    currency,
    {{ quote('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_EXCHANGE_RATE_HASHID') }}
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', 'airbyte_raw_exchange_rate') }}

