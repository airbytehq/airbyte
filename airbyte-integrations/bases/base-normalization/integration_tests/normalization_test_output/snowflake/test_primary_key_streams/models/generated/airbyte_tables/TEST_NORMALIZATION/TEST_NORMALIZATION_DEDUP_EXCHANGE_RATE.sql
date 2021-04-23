{{ config(alias="DEDUP_EXCHANGE_RATE", schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    HKD,
    NZD,
    USD,
    _airbyte_emitted_at,
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('TEST_NORMALIZATION_DEDUP_EXCHANGE_RATE_SCD') }}
-- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where _airbyte_active_row = True

