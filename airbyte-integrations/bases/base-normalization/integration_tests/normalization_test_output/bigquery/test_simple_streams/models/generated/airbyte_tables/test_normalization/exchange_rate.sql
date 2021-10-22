{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    currency,
    date,
    timestamp_col,
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}

