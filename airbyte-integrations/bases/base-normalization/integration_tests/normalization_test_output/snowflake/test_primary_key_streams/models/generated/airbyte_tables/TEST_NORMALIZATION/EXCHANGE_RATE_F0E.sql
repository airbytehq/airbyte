{{ config(alias="EXCHANGE_RATE", schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    NZD,
    USD,
    _airbyte_emitted_at,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from {{ ref('EXCHANGE_RATE_AB3_E8C') }}
-- EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_EXCHANGE_RATE') }}

