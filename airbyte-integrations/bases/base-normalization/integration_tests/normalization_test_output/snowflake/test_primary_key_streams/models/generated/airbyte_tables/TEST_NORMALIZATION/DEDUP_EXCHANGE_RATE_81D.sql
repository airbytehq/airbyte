{{ config(alias="DEDUP_EXCHANGE_RATE", schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    NZD,
    USD,
    _airbyte_emitted_at,
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('DEDUP_EXCHANGE_RATE_SCD_81D') }}
-- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where _airbyte_active_row = True

